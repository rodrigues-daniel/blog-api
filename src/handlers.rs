use actix_web::{web, HttpResponse, Responder};
use diesel::prelude::*;
use diesel::r2d2::{self, ConnectionManager};
use crate::models::{Post, NewPost};
use crate::schema::posts;

type DbPool = r2d2::Pool<ConnectionManager<SqliteConnection>>;

// Criar um novo post
pub async fn create_post(
    pool: web::Data<DbPool>,
    new_post: web::Json<NewPost>,
) -> impl Responder {
    let conn = pool.get().expect("Não foi possível obter conexão com o banco de dados");

    let new_post = NewPost {
        title: new_post.title.clone(),
        content: new_post.content.clone(),
        published: new_post.published,
    };

    let post = diesel::insert_into(posts::table)
        .values(&new_post)
        .get_result::<Post>(&conn)
        .expect("Erro ao inserir post");

    HttpResponse::Created().json(post)
}

// Listar todos os posts
pub async fn get_posts(pool: web::Data<DbPool>) -> impl Responder {
    let conn = pool.get().expect("Não foi possível obter conexão com o banco de dados");

    let posts = posts::table.load::<Post>(&conn).expect("Erro ao carregar posts");
    HttpResponse::Ok().json(posts)
}

// Obter um post por ID
pub async fn get_post_by_id(
    pool: web::Data<DbPool>,
    path: web::Path<i32>,
) -> impl Responder {
    let conn = pool.get().expect("Não foi possível obter conexão com o banco de dados");
    let post_id = path.into_inner();

    let post = posts::table
        .find(post_id)
        .first::<Post>(&conn)
        .optional()
        .expect("Erro ao buscar post");

    match post {
        Some(post) => HttpResponse::Ok().json(post),
        None => HttpResponse::NotFound().body("Post não encontrado"),
    }
}

// Atualizar um post
pub async fn update_post(
    pool: web::Data<DbPool>,
    path: web::Path<i32>,
    updated_post: web::Json<NewPost>,
) -> impl Responder {
    let conn = pool.get().expect("Não foi possível obter conexão com o banco de dados");
    let post_id = path.into_inner();

    let updated_post = diesel::update(posts::table.find(post_id))
        .set((
            posts::title.eq(&updated_post.title),
            posts::content.eq(&updated_post.content),
            posts::published.eq(updated_post.published),
        ))
        .get_result::<Post>(&conn)
        .optional()
        .expect("Erro ao atualizar post");

    match updated_post {
        Some(post) => HttpResponse::Ok().json(post),
        None => HttpResponse::NotFound().body("Post não encontrado"),
    }
}

// Excluir um post
pub async fn delete_post(
    pool: web::Data<DbPool>,
    path: web::Path<i32>,
) -> impl Responder {
    let conn = pool.get().expect("Não foi possível obter conexão com o banco de dados");
    let post_id = path.into_inner();

    let deleted_post = diesel::delete(posts::table.find(post_id))
        .get_result::<Post>(&conn)
        .optional()
        .expect("Erro ao excluir post");

    match deleted_post {
        Some(_) => HttpResponse::NoContent().finish(),
        None => HttpResponse::NotFound().body("Post não encontrado"),
    }
}