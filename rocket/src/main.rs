#![feature(proc_macro_hygiene, decl_macro)]

use rocket::{get, post, routes};

use serde::{Deserialize, Serialize};

use lazy_static::lazy_static;
use rocket::config::{Config, Environment};
use rocket_contrib::json::Json;

use std::fs::File;

lazy_static! {
    static ref CONFIG_FILE: String = { dotenv::var("CONFIG_FILE").expect("No env file!") };
}

#[derive(Serialize, Deserialize, Debug)]
struct MirrorConfig {
    use_humidity: bool,
    display_host_ip: bool,
    display_sleep_timer: bool,
    display_debug_panel: bool,
    sleep_timeout_sec: usize,
    screen_max_frame_rate: f32,
    ambient_temp_delay: usize,
}

#[get("/config")]
fn config() -> Result<Json<MirrorConfig>, std::io::Error> {
    let file = File::open(&*CONFIG_FILE)?;

    let conf = serde_json::from_reader(file)?;

    Ok(Json(conf))
}

#[post("/config", data = "<config>")]
fn submit(config: Json<MirrorConfig>) -> Result<(), serde_json::error::Error> {
    let mut file = File::create(&*CONFIG_FILE).unwrap();
    serde_json::to_writer_pretty(&mut file, &config.into_inner())
}

fn main() {
    let config = Config::build(Environment::Staging)
        .address("0.0.0.0")
        .port(8000)
        .finalize()
        .expect("Failed to build config");

    rocket::custom(config)
        .mount("/", routes![config, submit])
        .launch();
}
