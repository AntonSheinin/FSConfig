% rebase('templates/main_menu.tpl')

<a rel="channels" href="#select_all">Select All</a>
<a rel="channels" href="#select_none">Select None</a>
<a rel="channels" href="#invert_selection">Invert Selection</a>

<form action="/choose-channels" method="POST"">
           <table>
	<fieldset id="channels">
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
	</fieldset>
           </table>
           <br>
           <input type='submit' value='Submit'>
</form>

<script type="text/javascript">
  $(document).ready(function() {
    // Select all
    $("a[href='#select_all']").click(function() {
      $("#" + $(this).attr('rel') + " input[type='checkbox']").attr('checked', true);
      return false;
    });

    // Select none
    $("a[href='#select_none']").click(function() {
      $("#" + $(this).attr('rel') + " input[type='checkbox']").attr('checked', false);
      return false;
    });

    // Invert selection
    $("a[href='#invert_selection']").click(function() {
      $("#" + $(this).attr('rel') + " input[type='checkbox']").each(function() {
        $(this).attr('checked', !$(this).attr('checked'));
      });
      return false;
    });
  });
</script>