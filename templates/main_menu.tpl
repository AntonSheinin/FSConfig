<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">

<style>
body {
  margin: 0;
  font-family: Arial, Helvetica, sans-serif;
}

.topnav {
  overflow: hidden;
  background-color: #333;
}

.topnav a {
  float: left;
  color: #f2f2f2;
  text-align: center;
  padding: 14px 16px;
  text-decoration: none;
  font-size: 17px;
}

.topnav a:hover {
  background-color: #ddd;
  color: black;
}

.topnav a.active {
  background-color: #04AA6D;
  color: white;
}
</style>
</head>
<body>

<div class="topnav">
  <a class="active" href="/choose-channels">Choose Channels</a>
  <a href="/dvr-settings">DVR Settings</a>
  <a href="/source-priority">Source Priority</a>
  <a href="/stream-sorting">Stream Sorting</a>
  <a href="/config-upload-json">Config Upload JSON</a>
   <a href="/config-download-json">Config Download JSON</a>
   <a href="/config-upload-api">Config Upload API</a>

</div>

<br><br>

% if defined ('base') :
     {{!base}}

</body>
</html>