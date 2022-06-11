% rebase('views/main_menu.tpl')

<form action="/choose-channels" method="POST"">
           <table>
	      % for name in names:
		<tr>
        	   	          <td>
            			 <label for="{{name}}">{{name}}</label>
		          </td>
		          <td>
            			 <input type="checkbox" name="{{name}}" checked />
            		          </td>
		</tr>
    	     % end
           </table>

           <input type='submit' value='Submit'>
</form>