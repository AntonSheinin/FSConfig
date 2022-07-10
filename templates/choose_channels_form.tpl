% rebase('templates/main_menu.tpl')

<button type="button" onclick="#select_all">Select All</button>

<a rel="channels" href="#select_all">Select All</a>
<a rel="channels" href="#select_none">Select None</a>
<a rel="channels" href="#invert_selection">Invert Selection</a>

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
  $(document).ready(function() {
    // Select all
    $("a[href='#select_all']").click(function() {
      $("#" + $(this).prop('rel') + " input[type='checkbox']").prop('checked', true)
      return false;
    });

    // Select none
    $("a[href='#select_none']").click(function() {
      $("#" + $(this).prop('rel') + " input[type='checkbox']").prop('checked', false);
      return false;
    });

    // Invert selection
    $("a[href='#invert_selection']").click(function() {
      $("#" + $(this).prop('rel') + " input[type='checkbox']").each(function() {
        $(this).prop('checked', !$(this).prop('checked'));
      });
      return false;
    });
  });
</script>