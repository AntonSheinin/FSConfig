% rebase('views/main_menu.tpl')

<form action="/stream-sorting" method="POST"">
           <table>
	      % for name in names:
		<tr>
		          <td>
            			 <label for="{{name}}">{{name}}</label>
		          </td>
        	   	          <td>
			 <input type="number" name="{{name}}" min="1" max="1000" size="4">
            		          </td>
		</tr>
    	     % end
           </table>
           <br>
           <input type='submit' value='Submit'>
</form>