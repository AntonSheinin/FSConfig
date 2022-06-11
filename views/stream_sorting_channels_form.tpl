% rebase('views/main_menu.tpl')

<form action="/stream-sorting" method="POST"">
           <table>
	      % for name in names:
		<tr>
		          <td>
            			 <label for="{{name}}">{{name}}</label>
		          </td>
        	   	          <td>
			 <input type="number" name="{{name}}" />
            		          </td>
		</tr>
    	     % end
           </table>

           <input type='submit' value='Submit'>
</form>