% rebase('templates/main_menu.tpl')
<br>

<form action="/source-add" method="post" enctype="multipart/form-data">
	Username : <input type="text" name="username" required />
	Password :  <input type="text" name="password" required /><br><br>       
                  
 	<input type="submit" value="Submit" />
</form>