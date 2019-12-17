const apiUrl = "/api/config"
const attributes = {
    "use_humidity": "Use humidity sensor",
    "display_host_ip": "Display Host IP",
    "display_sleep_timer": "Display sleep timer",
    "display_debug_panel": "Display debug panel",
    "sleep_timeout_sec": "Time untill sleepmode (seconds)",
    "screen_max_frame_rate": "Max screen refresh rate (FPS)",
    "ambient_temp_delay": "Ambient temperature samplerate (seconds)",
}

const getConfig = () => {
    // For debug purposes
    loadResponseToForm({
        "use_humidity": true,
        "display_host_ip": true,
        "display_sleep_timer": true,
        "display_debug_panel": true,
        "sleep_timeout_sec": 20,
        "screen_max_frame_rate": 25,
        "ambient_temp_delay": 2,
    })

    // const url = "/api/config"
    // var xhttp = new XMLHttpRequest();

    // xhttp.onload = () => {
    //     clearForm()
    //     loadResponseToForm(xhttp.response)
    // };
    // xhttp.open("GET", url, true);
    // clearForm()
    // xhttp.send();
    // loadingNewConfigAnimation()
}

const getStreamGrab = () => {
    const url = "/api/stream"

    saveButton = document.getElementById("saveButton")
    loadButton = document.getElementById("loadButton")

    image = document.createElement("img")
    image.setAttribute("src", "screen_grab.jpeg")
    image.id = "thermalImage"
    image.onload = () => {
        saveButton.classList.remove("hideSaveButton");
        // saveButton.onclick = 
        image.setAttribute("alt", "Image of the thermal camera in the Smart Mirror");
    }

    image.onerror = () => {
        saveButton.classList.add("hideSaveButton");
        image.setAttribute("alt", "The thermal image could not be loaded.");
    }

    loadButton.onclick = () => {
        now = new Date
        image.setAttribute("src", "screen_grab.jpeg?" + now.getTime())
    }

    saveButton.onclick = () => {
        console.error("IMPLEMENT SAVE FUNCTION");
    }

    document.getElementById("imageBox").appendChild(image)
}

const submitConfig = (clickEvent) => {
    results = document.getElementById("form")

    httpBody = {}

    for (const result in results) {
        if (results.hasOwnProperty(result)) {
            const element = results[result];
            console.log(element.id, element.value);
            if (element.type == "checkbox") {
                httpBody[element.id] = element.checked
            } else {
                httpBody[element.id] = Number(element.value)
            }
        }
    }

    const url = "/api/config"
    var xhttp = new XMLHttpRequest();
    xhttp.onload = () => {
        clearForm()
        loadResponseToForm(xhttp.response)
        alert("New config has been saved")
    };
    xhttp.open("POST", url, true);
    xhttp.setRequestHeader("Content-Type", "application/json")
    clearForm()
    xhttp.send(JSON.stringify(httpBody));
    loadingNewConfigAnimation()
}

const resetConfig = (clickEvent) => {
    if (confirm("Are you sure? This will delete your current configuration.")) {
        const url = "/api/config"
        var xhttp = new XMLHttpRequest();
        xhttp.onload = () => {
            clearForm()
            loadResponseToForm(xhttp.response)
            alert("Config has been reset to DEFAULT values.")
        };
        xhttp.open("DELETE", url, true);
        clearForm()
        xhttp.send();
        loadingNewConfigAnimation()
    }
}

const clearForm = () => {
    document.getElementById("form").innerHTML = ""
}

const loadingNewConfigAnimation = () => {
    form = document.getElementById("form")
    loadingbox = document.createElement("div")
    loadingbox.classList.add("loadingbox")

    loadinginfo = document.createElement("div")
    loadinginfo.classList.add("loadinginfo")
    loadinginfo.innerHTML = "Loading configuration..."

    loadingAnimation = document.createElement("div")
    loadingAnimation.classList.add("loader")

    loadingbox.appendChild(loadinginfo)
    loadingbox.appendChild(loadingAnimation)

    form.appendChild(loadingbox)
}

const xmlHttpRequest = (requestType, callbackFunction, readyMessage, requestBody) => {
    const url = "/api/config"
    var xhttp = new XMLHttpRequest();

    xhttp.onload = () => {
        console.warn(xhttp.response)

        clearForm()
        alert(readyMessage)
        callbackFunction(xhttp.response)
    };
    xhttp.open(requestType, url, true);
    xhttp.setRequestHeader("Content-Type", "application/json")
    clearForm()
    xhttp.send(requestBody);
    loadingNewConfigAnimation()
}

const buildFormElement = (attribute, value, formElementType) => {
    let label = document.createElement("label")
    label.setAttribute("for", attribute)
    label.classList.add("attribute_field")
    label.innerHTML = attributes[attribute]

    let input = document.createElement("input")
    input.setAttribute("name", attribute)
    input.setAttribute("id", attribute)


    switch (formElementType) {
        case "boolean":
            input.setAttribute("type", "checkbox")
            input.classList.add("toggle")
            if (value) {
                input.setAttribute("checked", true)
            }
            // let toggle_label = document.createElement("label")
            // toggle_label.classList.add("toggle_label")

            // let toggle_switch = document.createElement("span")
            // toggle_switch.classList.add("toggle_switch")

            // toggle_label.appendChild(toggle_switch)

            label.appendChild(input)
            // label.appendChild(toggle_label)

            break;

        case "integer":
            input.setAttribute("type", "number")
            input.setAttribute("min", 0)
            input.classList.add("chars_input")
            input.value = value
            label.appendChild(input)
            break;

        default:
            input.setAttribute("type", "text")
            break;
    }

    let inputbox = document.createElement("div")
    inputbox.classList.add("formInputBox")
    inputbox.appendChild(label)

    document.getElementById("form").appendChild(inputbox)
}

const getFormElementType = (attribute) => {
    let formElementType
    switch (attribute) {
        case "use_humidity":
        case "display_host_ip":
        case "display_sleep_timer":
        case "display_debug_panel":
            formElementType = "boolean"
            break;

        case "sleep_timeout_sec":
        case "ambient_temp_delay":
        case "screen_max_frame_rate":
            formElementType = "integer"
            break

        default:
            console.warn("Invalid form element type!", attribute);
            break;
    }

    return formElementType
}

const setFormButtons = () => {
    let submitButton = document.createElement("span")
    submitButton.classList.add("button")
    submitButton.classList.add("submitbutton")
    submitButton.innerHTML = "Save"
    submitButton.addEventListener("click", submitConfig)

    let resetButton = document.createElement("span")
    resetButton.classList.add("button")
    resetButton.classList.add("resetbutton")
    resetButton.innerHTML = "Reset"
    resetButton.addEventListener("click", resetConfig)

    let buttonBox = document.createElement("div")
    buttonBox.classList.add("buttonbox")
    buttonBox.appendChild(resetButton)
    buttonBox.appendChild(submitButton)

    let form = document.getElementById("form")
    form.appendChild(buttonBox)
}

const loadResponseToForm = (response) => {
    if (typeof response == "string") {
        response = JSON.parse(response)
    }
    const configObject = response
    console.log("Starting form construction from response");
    for (const attribute in configObject) {
        if (configObject.hasOwnProperty(attribute)) {
            const value = configObject[attribute];
            const formElementType = getFormElementType(attribute)
            buildFormElement(attribute, value, formElementType)
        }
    }

    if (Object.keys(configObject).length > 0) {
        setFormButtons()
    } else {
        console.error("No attributes are returned to edit!");
    }

}

const main = () => {
    getStreamGrab()
    getConfig()
}

window.addEventListener("load", main)
