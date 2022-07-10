% rebase('templates/main_menu.tpl')

<form action="/stream-sorting" method="POST"">
           <table>
	      % for name in names:
		<tr>
		          <td>
            			 <label for="{{name}}">{{name}}</label>
		          </td>
        	   	          <td>
			 <input type="number" name="{{name}}" min="0" max="999" size="3">
            		          </td>
		</tr>
    	     % end
           </table>
           <br>
           <input type='submit' value='Submit'>
</form>