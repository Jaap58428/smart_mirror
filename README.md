# Smart Mirror
This is the main sourcecode repository for the Smart Mirror Sensortechnology project.

## Brief summery
The goal of this project is to make a mirror equipped with sensors, which help to monitor your health.
Whenever one stands in front of the mirror, the mirror detects this and wakes. The mirror then displays the temperature of the room, (optionally) the humidity of the room, and a thermal image of the person in front of the mirror.

## Project layout
There are mulptiple components in this project.
```
smart_mirror
|
+---> /python
|
+---> /rocket
|
+---> /static
|
+---> /startup
```

### Python
This component contains the main Python script for powering the mirror. This script is responsible for reading the sensors, and displaying the UI on the screen.

### Rocket
This component contains the backend for the configuration application. It is responsible for handling http requists made by the frontend contained in the static component.

### Static
This component contains the frontend for the configuration application. It is responsible for showing a usable web-interface used to configure the mirror.

### Startup
In this component, there are multiple scripts which are used to start the main python script, the rocket server, and a watcher to monitor changes 