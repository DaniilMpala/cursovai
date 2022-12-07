<html>
  <head>
    <title>App page</title>
    <link rel="stylesheet" href="style.css" type="text/css"/>
  </head>
  <body>
  <h3>Тест api</h3>
        <div>
            <h4>Вывод данных в json:</h4>
            <pre>
            <?php
            // echo json_encode($_POST);
            if (isset($_POST["endpoint"]) || isset($_GET["endpoint"]) ) {
                $myCurl = curl_init();
                if(isset($_POST["endpoint"])){
                  $tempEndPoint = $_POST["endpoint"];
                  unset($_POST["endpoint"]);
                  curl_setopt_array($myCurl, [
                    CURLOPT_URL =>"http://nginxserver/api/" .$tempEndPoint,
                    CURLOPT_RETURNTRANSFER => true,
                    CURLOPT_HEADER => false,
                    CURLOPT_CUSTOMREQUEST => "POST",
                    CURLOPT_POSTFIELDS => $_POST
                  ]);
                }else{
                  $tempEndPoint = $_GET["endpoint"];
                  unset($_GET["endpoint"]);
                  curl_setopt_array($myCurl, [
                    CURLOPT_URL =>"http://nginxserver/api/" .$tempEndPoint. '?' . http_build_query($_GET),
                    CURLOPT_RETURNTRANSFER => true,
                    CURLOPT_HEADER => false,
                    CURLOPT_CUSTOMREQUEST => "GET"
                  ]);
                }
                
                $response = curl_exec($myCurl);
                curl_close($myCurl);
                print_r(json_decode($response, true));
            } 
            ?>
            </pre>
        </div>
        <div>
            <h4>Добавить студента</h4>

            <form class="blockInputs" action="index.php" method="post">
              <input name="endpoint" value="addStudent" style="display:none" />
              <input name="fullName"  type="text" placeholder="fullName" />
              <input name="course"  type="number" placeholder="course" />
              <input name="group"  type="text" placeholder="group" />
              <button type="submit">Добавить</button>
            </form>

        </div>
        <div>
            <h4>Получить всех студентов</h4>

            <form class="blockInputs" action="index.php" method="get">
              <input name="endpoint" value="getStudent" style="display:none" />
              <input name="fullName"  type="text" placeholder="fullName" />
              <input name="course"  type="number" placeholder="course" />
              <input name="group"  type="text" placeholder="group" />
              <button type="submit">Получить</button>
            </form>

        </div>

        <div>
            <h4>Добавить практическую работу</h4>

            <form class="blockInputs" action="index.php" method="post">
              <input name="endpoint" value="addPracticalWork" style="display:none" />
              <input name="title"  type="text" placeholder="title" />
              <input name="subject"  type="text" placeholder="subject" />
              <button type="submit">Добавить</button>
            </form>

        </div>
        <div>
            <h4>Получить все практики</h4>

            <form class="blockInputs" action="index.php" method="get">
              <input name="endpoint" value="getPracticalWork" style="display:none" />
              <input name="title"  type="text" placeholder="title" />
              <input name="subject"  type="text" placeholder="subject" />
              <button type="submit">Получить</button>
            </form>

        </div>
        <div>
            <h4>Добавить сделанную практическую студентом</h4>

            <form class="blockInputs" action="index.php" method="post">
              <input name="endpoint" value="addCompletedWork" style="display:none" />
              <input name="idStudent"  type="number" placeholder="idStudent" />
              <input name="idPracticalWork"  type="number" placeholder="idPracticalWork" />
              <button type="submit">Добавить</button>
            </form>

        </div>
        <div>
            <h4>Получить все сделанные практики студента</h4>

            <form class="blockInputs" action="index.php" method="get">
              <input name="endpoint" value="getCompletedWork" style="display:none" />
              <input name="idStudent"  type="number" placeholder="idStudent" />
              <button type="submit">Получить</button>
            </form>

        </div>
      </body>
    </html>
