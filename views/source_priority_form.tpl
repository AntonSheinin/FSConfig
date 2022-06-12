% rebase('views/main_menu.tpl')

<br>

<form action="/source-priority" method="post" enctype="multipart/form-data">
	If URL contains  <input type="text" name="firstCondition" value="" />
	Than set priority on <input type="number" name="firstConditionPriority" size="4"/><br><br>

	If URL contains  <input type="text" name="secondCondition" value="" />
	Than set priority on <input type="number" name="secondConditionPriority" size="4"/><br><br>

	Else set priority on <input type="number" name="defaultPriority" value=2 size="4"/><br><br>       
                  
 	 <input type="submit" value="Submit" />
</form>