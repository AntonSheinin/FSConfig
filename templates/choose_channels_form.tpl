% rebase('templates/main_menu.tpl')

<button id="select_all" type="button" >Select All</button>
<button id="select_none" type="button" >Select None</button>
<button id="invert_none" type="button" >Invert selection</button>

<br><br>

<form action="/choose-channels" method="POST"">
           <table id="channels">
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
           <br>
       <input type='submit' value='Submit'>
</form>

<script type="text/javascript">
  $(function() {
          $('#select_all').click(function(){
             $("#channels  input[type='checkbox']").prop('checked', true)
             return false;
          });

          $('#select_none').click(function(){
             $("#" + "channels" + " input[type='checkbox']").prop('checked', false)
             return false;
          });

         $('#invert_selection').click(function() {
           $("#" + "channels" + " input[type='checkbox']").prop('checked', !$("#" + "channels" + " input[type='checkbox']").prop('checked'));
         });
         return false;
    });
  });
</script>