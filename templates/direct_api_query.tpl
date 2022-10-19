% rebase('templates/main_menu.tpl')
<br>

<form action="/direct-api-query" method="post" enctype="multipart/form-data">
    API Query : <input type="text" name="api_query" required /><br><br>

	Username : <input type="text" name="username" required />
	Password :  <input type="text" name="password" required /><br><br>       
                  
 	<input type="submit" value="Submit" />
</form>