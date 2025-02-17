use serde::{Serialize, Deserialize};
use chrono::NaiveDateTime;

#[derive(Debug, Serialize, Deserialize, Queryable, Insertable)]
#[diesel(table_name = crate::schema::posts)]
pub struct Post {
    pub id: Option<i32>,
    pub title: String,
    pub content: String,
    pub published: bool,
    pub created_at: NaiveDateTime,
}

#[derive(Debug, Serialize, Deserialize, Insertable)]
#[diesel(table_name = crate::schema::posts)]
pub struct NewPost {
    pub title: String,
    pub content: String,
    pub published: bool,
}