use std::borrow::Cow;
use std::fmt;
use std::mem::size_of;
use std::ops::Deref;

use bytemuck::{bytes_of, cast_slice, pod_read_unaligned};
use byteorder::{ByteOrder, NativeEndian};
use heed::{BoxedError, BytesDecode, BytesEncode};
use roaring::RoaringBitmap;

use crate::distance::Distance;
use crate::unaligned_vector::UnalignedVector;
use crate::ItemId;

#[derive(Clone, Debug)]
pub enum Node<'a, D: Distance> {
    Item(Item<'a, D>),
    Links(Links<'a>),
}

const NODE_TAG: u8 = 0;
const LINKS_TAG: u8 = 1;

impl<'a, D: Distance> Node<'a, D> {
    pub fn item(self) -> Option<Item<'a, D>> {
        if let Node::Item(item) = self {
            Some(item)
        } else {
            None
        }
    }

    pub fn links(self) -> Option<Links<'a>> {
        if let Node::Links(links) = self {
            Some(links)
        } else {
            None
        }
    }
}

/// An item node which corresponds to the vector inputed
/// by the user and the distance header.
pub struct Item<'a, D: Distance> {
    /// The header of this item.
    pub header: D::Header,
    /// The vector of this item.
    pub vector: Cow<'a, UnalignedVector<D::VectorCodec>>,
}

impl<D: Distance> fmt::Debug for Item<'_, D> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        f.debug_struct("Item").field("header", &self.header).field("vector", &self.vector).finish()
    }
}

impl<D: Distance> Clone for Item<'_, D> {
    fn clone(&self) -> Self {
        Self { header: self.header, vector: self.vector.clone() }
    }
}

impl<D: Distance> Item<'_, D> {
    /// Converts the item into an owned version of itself by cloning
    /// the internal vector. Doing so will make it mutable.
    pub fn into_owned(self) -> Item<'static, D> {
        Item { header: self.header, vector: Cow::Owned(self.vector.into_owned()) }
    }

    /// Builds a new item from a `Vec<f32>`.
    pub fn new(vec: Vec<f32>) -> Self {
        let vector = UnalignedVector::from_vec(vec);
        let header = D::new_header(&vector);
        Self { header, vector }
    }
}

#[derive(Clone, Debug)]
pub struct Links<'a> {
    pub links: Cow<'a, RoaringBitmap>,
}

impl<'a> Deref for Links<'a> {
    type Target = Cow<'a, RoaringBitmap>;
    fn deref(&self) -> &Self::Target {
        &self.links
    }
}

#[derive(Clone)]
pub struct ItemIds<'a> {
    bytes: &'a [u8],
}

impl<'a> ItemIds<'a> {
    pub fn from_slice(slice: &[u32]) -> ItemIds<'_> {
        ItemIds::from_bytes(cast_slice(slice))
    }

    pub fn from_bytes(bytes: &[u8]) -> ItemIds<'_> {
        ItemIds { bytes }
    }

    pub fn raw_bytes(&self) -> &[u8] {
        self.bytes
    }

    pub fn len(&self) -> usize {
        self.bytes.len() / size_of::<ItemId>()
    }

    pub fn iter(&self) -> impl Iterator<Item = ItemId> + 'a {
        self.bytes.chunks_exact(size_of::<ItemId>()).map(NativeEndian::read_u32)
    }
}

impl fmt::Debug for ItemIds<'_> {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        let mut list = f.debug_list();
        self.iter().for_each(|integer| {
            list.entry(&integer);
        });
        list.finish()
    }
}

/// The codec used internally to encode and decode nodes.
pub struct NodeCodec<D>(D);

impl<'a, D: Distance> BytesEncode<'a> for NodeCodec<D> {
    type EItem = Node<'a, D>;

    fn bytes_encode(item: &Self::EItem) -> Result<Cow<'a, [u8]>, BoxedError> {
        let mut bytes = Vec::new();
        match item {
            Node::Item(Item { header, vector }) => {
                bytes.push(NODE_TAG);
                bytes.extend_from_slice(bytes_of(header));
                bytes.extend(vector.as_bytes());
            }
            Node::Links(Links { links }) => {
                bytes.push(LINKS_TAG);
                links.serialize_into(&mut bytes)?;
            }
        }
        Ok(Cow::Owned(bytes))
    }
}

impl<'a, D: Distance> BytesDecode<'a> for NodeCodec<D> {
    type DItem = Node<'a, D>;

    fn bytes_decode(bytes: &'a [u8]) -> Result<Self::DItem, BoxedError> {
        match bytes {
            [NODE_TAG, bytes @ ..] => {
                let (header_bytes, remaining) = bytes.split_at(size_of::<D::Header>());
                let header = pod_read_unaligned(header_bytes);
                let vector = UnalignedVector::<D::VectorCodec>::from_bytes(remaining)?;

                Ok(Node::Item(Item { header, vector }))
            }
            [LINKS_TAG, bytes @ ..] => {
                let links: Cow<'_, RoaringBitmap> =
                    Cow::Owned(RoaringBitmap::deserialize_from(bytes).unwrap());
                Ok(Node::Links(Links { links }))
            }

            [unknown_tag, ..] => {
                Err(Box::new(InvalidNodeDecoding { unknown_tag: Some(*unknown_tag) }))
            }
            [] => Err(Box::new(InvalidNodeDecoding { unknown_tag: None })),
        }
    }
}

#[derive(Debug, thiserror::Error)]
pub struct InvalidNodeDecoding {
    unknown_tag: Option<u8>,
}

impl fmt::Display for InvalidNodeDecoding {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self.unknown_tag {
            Some(unknown_tag) => write!(f, "Invalid node decoding: unknown tag {unknown_tag}"),
            None => write!(f, "Invalid node decoding: empty array of bytes"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::{Item, Links, Node, NodeCodec};
    use crate::{distance::Cosine, internals::UnalignedVector, Distance};
    use heed::{BytesDecode, BytesEncode};
    use roaring::RoaringBitmap;
    use std::borrow::Cow;

    #[test]
    fn check_bytes_encode_decode() {
        type D = Cosine;

        let vector = UnalignedVector::from_vec(vec![1.0f32, 2.0f32]);
        let header = D::new_header(&vector);
        let item = Item { vector, header };
        let db_item = Node::Item(item);

        let bytes = NodeCodec::<D>::bytes_encode(&db_item);
        assert!(bytes.is_ok());
        let bytes = bytes.unwrap();
        dbg!("{}, {}", std::mem::size_of_val(&db_item), bytes.len());
        // dbg!("{:?}", &bytes);

        let db_item2 = NodeCodec::<D>::bytes_decode(bytes.as_ref());
        assert!(db_item2.is_ok());
        let db_item2 = db_item2.unwrap();

        dbg!("{:?}", &db_item2);
        dbg!("{:?}", &db_item);
    }

    #[test]
    fn test_codec() {
        type D = Cosine;

        let vector = UnalignedVector::from_vec(vec![1.0f32, 2.0f32]);
        let header = D::new_header(&vector);
        let item = Item { vector, header };
        let db_item = Node::Item(item.clone());

        let bytes = NodeCodec::<D>::bytes_encode(&db_item);
        assert!(bytes.is_ok());
        let bytes = bytes.unwrap();

        let new_item = NodeCodec::<D>::bytes_decode(bytes.as_ref());
        assert!(new_item.is_ok());
        let new_item = new_item.unwrap().item().unwrap();

        assert!(matches!(new_item.vector, Cow::Borrowed(_)));
        assert_eq!(new_item.vector.as_bytes(), item.vector.as_bytes());
    }

    #[test]
    fn test_bitmap_codec() {
        let mut bitmap = RoaringBitmap::new();
        bitmap.insert(1);
        bitmap.insert(42);

        let links = Links { links: Cow::Owned(bitmap) };
        let db_item = Node::Links(links);
        let bytes = NodeCodec::<Cosine>::bytes_encode(&db_item).unwrap();

        let node = NodeCodec::<Cosine>::bytes_decode(&bytes).unwrap();
        assert!(matches!(node, Node::Links(_)));
        let new_links = match node {
            Node::Links(links) => links,
            _ => unreachable!(),
        };
        assert!(new_links.links.contains(1));
        assert!(new_links.links.contains(42));
    }
}
