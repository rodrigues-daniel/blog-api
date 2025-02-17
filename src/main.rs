mod models;
mod handlers;
mod schema;

use actix_web::{App, HttpServer};
use diesel::r2d2::{self, ConnectionManager};
use diesel::SqliteConnection;

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    dotenv::dotenv().ok();
    let database_url = std::env::var("DATABASE_URL").expect("DATABASE_URL não definido");
    let manager = ConnectionManager::<SqliteConnection>::new(database_url);
    let pool = r2d2::Pool::builder()
        .build(manager)
        .expect("Falha ao criar pool de conexões");

    HttpServer::new(move || {
        App::new()
            .app_data(actix_web::web::Data::new(pool.clone()))
            .route("/posts", actix_web::web::post().to(handlers::create_post))
            .route("/posts", actix_web::web::get().to(handlers::get_posts))
            .route("/posts/{id}", actix_web::web::get().to(handlers::get_post_by_id))
            .route("/posts/{id}", actix_web::web::put().to(handlers::update_post))
            .route("/posts/{id}", actix_web::web::delete().to(handlers::delete_post))
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}