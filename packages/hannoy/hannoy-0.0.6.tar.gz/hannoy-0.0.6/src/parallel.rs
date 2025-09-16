use core::slice;
use std::borrow::Cow;
use std::marker;

use hashbrown::HashMap;
use heed::types::Bytes;
use heed::{BytesDecode, RoTxn};
use roaring::RoaringBitmap;
use rustc_hash::FxBuildHasher;
use tracing::debug;

use crate::internals::{Item, KeyCodec};
use crate::key::{Prefix, PrefixCodec};
use crate::node::{Links, Node, NodeCodec};
use crate::progress::HannoyBuild;
use crate::writer::BuildOption;
use crate::{Database, Distance, ItemId, LayerId};

/// A struture used to keep a list of the item nodes in the graph.
///
/// It is safe to share between threads as the pointer are pointing
/// in the mmapped file and the transaction is kept here and therefore
/// no longer touches the database.
pub struct ImmutableItems<'t, D> {
    items: HashMap<ItemId, *const u8, FxBuildHasher>,
    constant_length: Option<usize>,
    _marker: marker::PhantomData<(&'t (), D)>,
}

// NOTE: this previously took an arg `items: &RoaringBitmap` which corresponded to the `to_insert`.
// When building the hnsw in multiple dumps we need vecs from previous dumps in order to "glue"
// things together.
// To accomodate this we use a cursor over ALL Key::items in the db.
impl<'t, D: Distance> ImmutableItems<'t, D> {
    /// Creates the structure by fetching all the item vector pointers
    /// and keeping the transaction making the pointers valid.
    /// Do not take more items than memory allows.
    /// Remove from the list of candidates all the items that were selected and return them.
    pub fn new<P>(
        rtxn: &'t RoTxn,
        database: Database<D>,
        index: u16,
        options: &BuildOption<P>,
    ) -> heed::Result<Self>
    where
        P: steppe::Progress,
    {
        debug!("fetching the pointers to the items from lmdb");
        options.progress.update(HannoyBuild::FetchItemPointers);

        let mut map =
            HashMap::with_capacity_and_hasher(database.len(rtxn)? as usize, FxBuildHasher);
        let mut constant_length = None;

        let cursor = database
            .remap_types::<PrefixCodec, Bytes>()
            .prefix_iter(rtxn, &Prefix::item(index))?
            .remap_key_type::<KeyCodec>();

        for res in cursor {
            let (item_id, bytes) = res?;
            assert_eq!(*constant_length.get_or_insert(bytes.len()), bytes.len());
            let ptr = bytes.as_ptr();
            map.insert(item_id.node.item, ptr);
        }

        Ok(ImmutableItems { items: map, constant_length, _marker: marker::PhantomData })
    }

    /// Returns the items identified by the given ID.
    pub fn get(&self, item_id: ItemId) -> heed::Result<Option<Item<'t, D>>> {
        let len = match self.constant_length {
            Some(len) => len,
            None => return Ok(None),
        };
        let ptr = match self.items.get(&item_id) {
            Some(ptr) => *ptr,
            None => return Ok(None),
        };

        // safety:
        // - ptr: The pointer comes from LMDB. Since the database cannot be written to, it is still valid.
        // - len: All the items share the same dimensions and are the same size
        let bytes = unsafe { slice::from_raw_parts(ptr, len) };
        NodeCodec::bytes_decode(bytes).map_err(heed::Error::Decoding).map(|node| node.item())
    }
}

unsafe impl<D> Sync for ImmutableItems<'_, D> {}

/// A struture used to keep a list of all the links.
/// It is safe to share between threads as the pointers are pointing
/// in the mmapped file and the transaction is kept here and therefore
/// no longer touches the database.
pub struct ImmutableLinks<'t, D> {
    links: HashMap<(u32, u8), (usize, *const u8), FxBuildHasher>,
    _marker: marker::PhantomData<(&'t (), D)>,
}

impl<'t, D: Distance> ImmutableLinks<'t, D> {
    /// Creates the structure by fetching all the root pointers
    /// and keeping the transaction making the pointers valid.
    pub fn new<P>(
        rtxn: &'t RoTxn,
        database: Database<D>,
        index: u16,
        nb_links: u64,
        options: &BuildOption<P>,
    ) -> heed::Result<Self>
    where
        P: steppe::Progress,
    {
        debug!("fetching the pointers to the links from lmdb");
        options.progress.update(HannoyBuild::FetchLinksPointers);

        let mut links = HashMap::with_capacity_and_hasher(nb_links as usize, FxBuildHasher);

        let iter = database
            .remap_types::<PrefixCodec, Bytes>()
            .prefix_iter(rtxn, &Prefix::links(index))?
            .remap_key_type::<KeyCodec>();

        for result in iter {
            let (key, bytes) = result?;
            let links_id = key.node.unwrap_node();
            links.insert(links_id, (bytes.len(), bytes.as_ptr()));
        }

        Ok(ImmutableLinks { links, _marker: marker::PhantomData })
    }

    /// Returns the node identified by the given ID.
    pub fn get(&self, item_id: ItemId, level: LayerId) -> heed::Result<Option<Links<'t>>> {
        let key = (item_id, level);
        let (ptr, len) = match self.links.get(&key) {
            Some((len, ptr)) => (*ptr, *len),
            None => return Ok(None),
        };

        // safety:
        // - ptr: The pointer comes from LMDB. Since the database cannot be written to, it is still valid.
        // - len: The len cannot change either
        let bytes = unsafe { slice::from_raw_parts(ptr, len) };
        NodeCodec::bytes_decode(bytes)
            .map_err(heed::Error::Decoding)
            .map(|node: Node<'t, D>| node.links())
    }

    pub fn iter(
        &self,
    ) -> impl Iterator<Item = heed::Result<((ItemId, u8), Cow<'_, RoaringBitmap>)>> {
        self.links.keys().map(|&k| {
            let (item_id, level) = k;
            match self.get(item_id, level) {
                Ok(Some(Links { links })) => Ok((k, links)),
                Ok(None) => {
                    unreachable!("link at level {level} with item_id {item_id} not found")
                }
                Err(e) => Err(e),
            }
        })
    }

    /// `Iter`s only over links in a given level
    pub fn iter_layer(
        &self,
        layer: u8,
    ) -> impl Iterator<Item = heed::Result<((ItemId, u8), Cow<'_, RoaringBitmap>)>> {
        self.links.keys().filter_map(move |&k| {
            let (item_id, level) = k;
            if level != layer {
                return None;
            }

            match self.get(item_id, level) {
                Ok(Some(Links { links })) => Some(Ok((k, links))),
                Ok(None) => {
                    unreachable!("link at level {level} with item_id {item_id} not found")
                }
                Err(e) => Some(Err(e)),
            }
        })
    }
}

unsafe impl<D> Sync for ImmutableLinks<'_, D> {}
