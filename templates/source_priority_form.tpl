% rebase('templates/main_menu.tpl')

<form action="/source-priority" method="post" enctype="multipart/form-data">
	If URL contains  			<input type="text" name="first_condition" value="" />
	Than set priority on (0-9) 	<input type="number" name="first_condition_priority" size="4" min="0" max="9"/><br><br>

	If URL contains  			<input type="text" name="second_condition" value="" />
	Than set priority on (0-9) 	<input type="number" name="second_condition_priority" size="4" min="0" max="9"/><br><br>

	Else set priority on (0-9) 	<input type="number" name="default_priority" value=2 size="4" min="0" max="9"/><br><br>       
                  
 	<input type="submit" value="Submit" />
</form>