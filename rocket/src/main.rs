#![feature(proc_macro_hygiene, decl_macro)]

use rocket::{catch, catchers, delete, get, post, request::Request, response::NamedFile, routes};

use serde::{Deserialize, Serialize};

use lazy_static::lazy_static;
use rocket_contrib::json::Json;

use std::{
    fs::{File},
    io::{self, Write},
};

mod cors;

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
            use_humidity: true,
            display_host_ip: true,
            display_sleep_timer: true,
            display_debug_panel: true,
            sleep_timeout_sec: 30,
            screen_max_frame_rate: 60.0,
            ambient_temp_delay: 10,
        }
    }
}

impl MirrorConfig {
    fn to_writer_pretty(&self, writer: &mut impl Write) -> Result<(), serde_json::error::Error> {
        serde_json::to_writer_pretty(writer, self)
    }
}

#[get("/config")]
fn config() -> Json<MirrorConfig> {
    let config = File::open(&*CONFIG_FILE)
        .and_then(|file| serde_json::from_reader(file).map_err(Into::into))
        .unwrap_or_default();

    Json(config)
}

#[post("/config", format = "application/json", data = "<config>")]
fn submit(config: Json<MirrorConfig>) -> Result<Json<MirrorConfig>, io::Error> {
    let mut file = File::create(&*CONFIG_FILE)?;

    config.to_writer_pretty(&mut file)?;
    
    let _ = file.sync_all()?;
    Ok(config)
}

#[delete("/config")]
fn reset() -> Result<Json<MirrorConfig>, io::Error> {
    let mut file = File::create(&*CONFIG_FILE)?;

    let default_config = MirrorConfig::default();
    default_config.to_writer_pretty(&mut file)?;

    let _ = file.sync_all()?;
    Ok(Json(default_config))
}

#[get("/")]
fn index() -> io::Result<NamedFile> {
    NamedFile::open("/home/jaap/smart_mirror/static/index.html")
}

#[catch(404)]
fn not_found(req: &Request) -> String {
    format!("I couldn't find '{}'. Try something else?", req.uri())
}

#[catch(500)]
fn internal_error() -> &'static str {
    "Whoops! Looks like we messed up."
}

fn main() {
    use rocket_contrib::serve::StaticFiles;

    rocket::ignite()
        .register(catchers![internal_error, not_found])
        //.mount("/", routes![index])
        .mount("/", StaticFiles::from("/home/jaap/smart_mirror/static"))
        .mount("/api", routes![config, submit, reset])
        .attach(cors::make_cors())
        .launch();
}
