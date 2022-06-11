% rebase('views/main_menu.tpl')

<br>

<form action="/source-priority" method="post" enctype="multipart/form-data">
	If URL contains  <input type="text" name="firstCondition" value="" />
	Than set priority on <input type="number" name="firstConditionPriority" /><br><br>

	If URL contains  <input type="text" name="secondCondition" value="" />
	Than set priority on <input type="number" name="secondConditionPriority" /><br><br>

	Else set priority on <input type="number" name="defaultPriority" value=2 /><br><br>       
                  
 	 <input type="submit" value="Submit" />
</form>