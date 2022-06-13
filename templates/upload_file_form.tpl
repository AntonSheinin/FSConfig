% rebase('views/main_menu.tpl')

<form action="/config-upload" method="post" enctype="multipart/form-data">
	Select a .json config file:     <input type="file" name="config" required/>
 	                                                  <input type="submit" value="Upload" />
</form>