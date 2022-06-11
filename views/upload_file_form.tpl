% rebase('views/main_menu.tpl')

<p><br /></p>

<form action="/config-upload" method="post" enctype="multipart/form-data">
	Select a config file:     <input type="file" name="config" />
 	                                        <input type="submit" value="Upload" />
</form>