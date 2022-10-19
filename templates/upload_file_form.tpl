% rebase('templates/main_menu.tpl')

<form action="/config-load-json" method="post" enctype="multipart/form-data">
	Select a .json config file:     <input type="file" name="config" required/><br>
 	                                <input type="submit" value="Upload" />
</form>