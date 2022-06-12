% rebase('views/main_menu.tpl')

<form action="/source-priority" method="post" enctype="multipart/form-data">
	If URL contains  <input type="text" name="firstCondition" value="" />
	Than set priority on (0-9) <input type="number" name="firstConditionPriority" size="4" min="0" max="9"/><br><br>

	If URL contains  <input type="text" name="secondCondition" value="" />
	Than set priority on (0-9) <input type="number" name="secondConditionPriority" size="4" min="0" max="9"/><br><br>

	Else set priority on (0-9) <input type="number" name="defaultPriority" value=2 size="4" min="0" max="9"/><br><br>       
                  
 	 <input type="submit" value="Submit" />
</form>