#![feature(proc_macro_hygiene, decl_macro)]

use rocket::{get, post, routes};

use serde::{Deserialize, Serialize};

use lazy_static::lazy_static;
use rocket::config::{Config, Environment};
use rocket_contrib::json::Json;

use std::fs::File;

lazy_static! {
    static ref CONFIG_FILE: String =
        dotenv::var("CONFIG_FILE").unwrap_or_else(|_| String::from("config.config"));
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

impl Default for MirrorConfig {
    #[inline(always)]
    fn default() -> Self {
        MirrorConfig {
            use_humidity: false,
            display_host_ip: true,
            display_sleep_timer: false,
            display_debug_panel: false,
            sleep_timeout_sec: 10,
            screen_max_frame_rate: 0.033,
            ambient_temp_delay: 2,
        }
    }
}

#[get("/config")]
fn config() -> Json<MirrorConfig> {
    let config = File::open(&*CONFIG_FILE)
        .and_then(|file| serde_json::from_reader(file).map_err(|e| e.into()))
        .unwrap_or_default();

    Json(config)
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
