table! {
    posts (id) {
        id -> Nullable<Integer>,
        title -> Text,
        content -> Text,
        published -> Bool,
        created_at -> Timestamp,
    }
}