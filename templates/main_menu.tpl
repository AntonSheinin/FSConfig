<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="https://code.jquery.com/jquery-3.6.0.slim.min.js" integrity="sha256-u7e5khyithlIdTpu22PHhENmPcRdFiHRjhAuHcs05RI=" crossorigin="anonymous"></script>

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
    font-size: 14px;
  }

  .topnav a:hover {
    background-color: #ddd;
    color: black;
  }

  .topnav a.active {
    background-color: #ffa500;
    color: black;
  }
  </style>
</head>

<body>

  <div class="topnav">
    <a class="active" href="/choose-channels">Choose Channels</a>
    <a href="/direct-api-query">Direct API Query</a>
    <a href="/dvr-settings">DVR Settings</a>
    <a href="/source-priority">Source Priority</a>
    <a href="/stream-sorting">Stream Sorting</a>
    <a href="/config-load-json">Load Config File</a>
    <a href="/config-download-json">Download Config File</a>
    <a href="/config-upload-api">Upload Config to Server</a>
    <a href="/config-load-api">Load Config from Server</a>
  </div>

  <br><br>

  % if defined ('base') :
    {{!base}}

</body>
</html>