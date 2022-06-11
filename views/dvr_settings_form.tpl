% rebase('views/main_menu.tpl')

<br>

<form action="/dvr-settings" method="post" enctype="multipart/form-data">
	DVR storage path     <input type="text" name="path" value="/mnt/storage/storage" /><br><br>
	Disc space (Gb)	<input type="number" name="space" value=600 /><br><br>
                  Archive duration       <select name="duration" id="duration">
				<option value="0">None</option>
    				<option value="3600">1 hour</option>
    				<option value="86400">1 day</option>
    				<option value="604800">1 week</option>
    				<option value="1209600">2 weeks</option>
  			</select>
			<br><br>
                  
 	 <input type="submit" value="Submit" />
</form>