use proptest::prelude::*;
use rand::{rngs::StdRng, seq::SliceRandom, thread_rng, Rng, SeedableRng};
use roaring::RoaringBitmap;

use crate::{
    distance::{BinaryQuantizedCosine, Cosine},
    tests::{create_database, create_database_indices_with_items, rng, DatabaseHandle},
    Reader, Writer,
};

const M: usize = 16;
const M0: usize = 32;

// Minimal reproducer for issue #78
// <https://github.com/nnethercott/hannoy/issues/78>
#[test]
fn quantized_iter_has_right_dimensions() {
    let DatabaseHandle { env, database, tempdir: _ } = create_database::<BinaryQuantizedCosine>();
    let mut wtxn = env.write_txn().unwrap();
    // use a prime number of dims
    const DIM: usize = 1063;
    let writer = Writer::new(database, 0, DIM);

    let mut rng = StdRng::seed_from_u64(42);

    let mut vec = [0f32; DIM];
    rng.fill(&mut vec);
    writer.add_item(&mut wtxn, 0, &vec).unwrap();
    writer.builder(&mut rng).build::<M, M0>(&mut wtxn).unwrap();
    wtxn.commit().unwrap();

    let rtxn = env.read_txn().unwrap();
    let reader = Reader::open(&rtxn, 0, database).unwrap();
    let mut cursor = reader.iter(&rtxn).unwrap();
    let (_, new_vec) = cursor.next().unwrap().unwrap();

    assert!(new_vec.len() == DIM);
}

#[test]
fn search_on_candidates_has_right_num() {
    const DIM: usize = 768;
    let db_indexes = 1..5;

    let DatabaseHandle { env, database, tempdir: _ } =
        create_database_indices_with_items::<Cosine, DIM, M, M0, _>(
            db_indexes.clone(),
            1000,
            &mut rng(),
        );

    let rtxn = env.read_txn().unwrap();
    let mut rng = rng();
    let mut shuffled_indices = Vec::from_iter(db_indexes);
    shuffled_indices.shuffle(&mut rng);

    for index in shuffled_indices {
        let reader = crate::Reader::<Cosine>::open(&rtxn, index, database).unwrap();

        // search with 10 candidates
        let mut query = [f32::default(); DIM];
        rng.fill(&mut query);

        let c: [u32; 10] = std::array::from_fn(|_| thread_rng().gen::<u32>() % 1000);
        let candidates = RoaringBitmap::from_iter(c);
        let found = reader.nns(10).candidates(&candidates).by_vector(&rtxn, &query).unwrap();
        assert_eq!(&RoaringBitmap::from_iter(found.into_iter().map(|(i, _)| i)), &candidates);

        // search with 1 candidate
        let c: [u32; 1] = std::array::from_fn(|_| thread_rng().gen::<u32>() % 1000);
        let candidates = RoaringBitmap::from_iter(c);
        let found = reader.nns(1).candidates(&candidates).by_vector(&rtxn, &query).unwrap();
        assert_eq!(&RoaringBitmap::from_iter(found.into_iter().map(|(i, _)| i)), &candidates);
    }
}

fn all_items_are_reachable<const M: usize, const M0: usize>(n: usize) {
    const DIM: usize = 768;
    let mut rng = rng();

    let DatabaseHandle { env, database, tempdir: _ } =
        create_database_indices_with_items::<Cosine, DIM, M, M0, _>(0..1, n, &mut rng);
    let rtxn = env.read_txn().unwrap();

    // Check that all items were written correctly
    let reader = crate::Reader::<Cosine>::open(&rtxn, 0, database).unwrap();
    assert_eq!(reader.item_ids().len(), n as u64);
    assert!((0..n as u32).all(|i| reader.contains_item(&rtxn, i).unwrap()));

    let found = reader.nns(n).ef_search(n).by_vector(&rtxn, &[0.0; DIM]).unwrap();
    assert_eq!(&RoaringBitmap::from_iter(found.into_iter().map(|(id, _)| id)), reader.item_ids())
}

proptest! {
    #![proptest_config(ProptestConfig {
            cases: 10,.. ProptestConfig::default()
    })]

    #[test]
    fn all_items_are_reachable_3_3(n in 1..10000usize){
        all_items_are_reachable::<6,6>(n);
    }
}
