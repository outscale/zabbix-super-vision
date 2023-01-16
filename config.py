
CONTENT = {}

LIST_SEVERITY = {
'0': 'Not classified',
'1': 'Information',
'2': 'Warning',
'3': 'Average',
'4': 'High',
'5': 'Disaster'
}

TOTAL_ALERTS = "0"

TEMPLATE_HEAD = '''<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <title>[alerts] Super(vision)</title>
    <link rel="stylesheet" href="/css/bootstrap.min.css">
    <link rel="stylesheet" href="/css/octicons.min.css">
    <link rel="stylesheet" href="/css/offline.css">
    <script src="/js/jquery-3.4.1.slim.min.js"></script>
    <script type="text/javascript" src="/js/dynafav-1.0.js"></script>
    <script src="/js/popper.min.js"></script>
    <script src="/js/bootstrap.min.js"></script>
    <script src="/js/offline.min.js" ></script>
    <style type="text/css">
      a { color: #DF7401;
          font-weight: bolder;
      }
      a:hover {
         text-decoration: none;
         color: #DF7401;
      }
      body {
         background-color: #333;
         font-weight: bolder;
      }
      .disaster {
        background-color:#D30801;
        color:white;
      }
      .table td, .table th { padding: 1px; !important }
      .image-container {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 15%;
      }
      .image-mexico {
        display: flex;
        justify-content: center;
        align-items: center;
        padding-top: 5%;
      }
      .btn-group-sm>.btn, .btn-sm {
        padding: .08rem .5rem;
      }
    </style>
  </head>
<body>
NAVBAR
  <div class="row-fluid">
    <div class="container">
        <div class="collapse" id="form-msg">
          <div class="card card-body">
            <form action="/post" method="post" accept-charset="utf-8" enctype="application/x-www-form-urlencoded">
              <div class="form-row">
                <div class="col">
                 <input type="text" class="form-control" placeholder="Your name" name="name" required>
               </div>
               <div class="col">
                 <input type="text" class="form-control" placeholder="Message" name="msg" required>
                 <input type="text" class="form-control" name="url" id="url" hidden readonly>
              </div>
              <div class="col">
                <select class="form-control" name="lvl">
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="danger">Disaster</option>
                </select>
              </div>
              FORM_TEAM
              <div class="col">
                <button id="publish" name="save" class="btn btn-secondary">Publish <span class="octicon octicon-mail"></span></button>
              </div>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
  <!--<div class="row-fluid">
    <div class="container-fluid">
      NOTES
    </div>
  </div>-->
  <div class="row-fluid">
    <div class="container-fluid">
      CHECK
      NOTES
      <table class="table table-dark table-sm alerts">'''
TEMPLATE_FOOTER='''
      </table>
    </div>
  </div>
</body>
  <script type="text/javascript">
    var refresh;
    $(document).ready(function() {
      $('nav').show();
      $('form').show();
      $('#url').val($(location).attr('href'));
      $('.url_note').val($(location).attr('href'));
      $('#del_note').click(function(e)
      {
        if(!confirm("This note will be deleted. Are you sure?"))
    {
        e.preventDefault();
    }
});
      function reload_page() {
        if(Offline.state != 'up') {
          clearInterval(refresh);
        } else {
          var refresh;
          location.reload();
        }
      }

      refresh = setInterval(reload_page,20000);

      Offline.options = {
        // to check the connection status immediatly on page load.
        checkOnLoad: true,
        // to monitor AJAX requests to check connection.
        interceptRequests: true,
        // to automatically retest periodically when the connection is down (set to false to disable).
        reconnect: {
         // delay time in seconds to wait before rechecking.
         initialDelay: 3,
         // wait time in seconds between retries.
         delay: 10
       },
       // to store and attempt to remake requests which failed while the connection was down.
       requests: true
     };
    });
  </script>
</html>
'''

COLOR_TEAM = {
	"Discovered hosts":					"#04B404;",
	"Linux servers":					"#DD90F2;",
	"Zabbix servers":					"#F290E8;"
}

NAVBAR = '''
<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
  <a class="navbar-brand" href="/">[0] Super(Vision)</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarSupportedContent">
    <ul class="navbar-nav mr-auto">
      LIST
    </ul>
      <button class="btn btn-outline-secondary" type="button" data-toggle="collapse" data-target="#form-msg" aria-expanded="false" aria-controls="form-message">Add message <span class='octicon octicon-comment'></span></button>
  </div>
</nav>
'''
