const attributes = {
    "use_humidity": "Use humidity",
    "display_host_ip": "Display Host IP",
    "display_sleep_timer": "Display sleep timer",
    "display_debug_panel": "Display debug panel",
    "sleep_timeout_sec": "Time untill sleepmode in seconds",
    "screen_max_frame_rate": "Max screen refresh rate (FPS)",
    "ambient_temp_delay": "Ambient temperature samplerate in seconds",
}

const customSubmit = (clickEvent) => {
    results = document.getElementById("form")
    console.log(results);

    for (const result in results) {
        if (results.hasOwnProperty(result)) {
            const element = results[result];
            console.log(result, element.value);

        }
    }
}

const buildFormElement = (attribute, value, formElementType) => {
    let label = document.createElement("label")
    label.setAttribute("for", attribute)
    label.innerHTML = attributes[attribute]

    let input = document.createElement("input")
    input.setAttribute("name", attribute)
    input.setAttribute("id", attribute)

    label.appendChild(input)

    switch (formElementType) {
        case "boolean":
            input.setAttribute("type", "checkbox")
            if (value) {
                input.setAttribute("checked", true)
            }
            label.classList.add("clickable")
            break;

        case "integer":
            input.setAttribute("type", "number")
            input.setAttribute("min", 0)
            input.setAttribute("max", 120)
            input.setAttribute("step", 1)
            input.value = value
            break;
        case "float":
            input.setAttribute("type", "number")
            input.setAttribute("min", 0)
            input.setAttribute("max", 1)
            input.setAttribute("step", 0.001)
            input.value = value
            break;

        default:
            input.setAttribute("type", "text")
            break;
    }

    let inputbox = document.createElement("div")
    inputbox.classList.add("formInputBox")
    inputbox.appendChild(label)

    document.getElementById("form").appendChild(inputbox)
    // Add element to DOM

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
            formElementType = "integer"
            break;

        case "screen_max_frame_rate":
            formElementType = "float"

        default:
            console.warn("Invalid form element type!", attribute);
            break;
    }

    return formElementType
}

const resetConfig = (clickEvent) => {
    form = document.getElementById("form")
    console.log(form);
    
}

const setFormButtons = (configObject) => {
    let submitButton = document.createElement("span")
    submitButton.classList.add("button")
    submitButton.classList.add("submitbutton")
    submitButton.innerHTML = "Save"
    submitButton.addEventListener("click", customSubmit)

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

const loadConfigToForm = (response) => {
    // const configObject = JSON.parse(response)
    const configObject = response
    console.log("Starting form construct loop through response");
    for (const attribute in configObject) {
        if (configObject.hasOwnProperty(attribute)) {
            const value = configObject[attribute];
            console.log("Building form element for:", attribute);
            const formElementType = getFormElementType(attribute)
            buildFormElement(attribute, value, formElementType)
        }
    }

    if (Object.keys(configObject).length > 0) {
        setFormButtons(configObject)
    } else {
        console.warn("No attributes are returned to edit!");
    }

}

const getCurrentConfig = (configGetUrl) => {
    console.log("Building config fetch");
    var xhttp = new XMLHttpRequest();
    xhttp.onreadystatechange = () => {
        if (this.readyState == 4 && this.status == 200) {
            console.log("Succesfull response:");
            console.log(xhttp.response);
            loadConfigToForm(response)
        }
    };
    xhttp.open("GET", configGetUrl, true);
    // xhttp.send();
    console.log("Fetching config from Smart Mirror...", configGetUrl);


    // PURE FOR DEBUG PURPOSES, REMOVE LATER
    response = {
        "use_humidity": false,
        "display_host_ip": true,
        "display_sleep_timer": false,
        "display_debug_panel": false,
        "sleep_timeout_sec": 10,
        "screen_max_frame_rate": 0.033,
        "ambient_temp_delay": 2,
    }
    loadConfigToForm(response)
}

const main = () => {
    console.log("Page has loaded");
    const configGetUrl = "./mock_response.json"
    getCurrentConfig(configGetUrl)
}

window.addEventListener("load", main)