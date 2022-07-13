% rebase('templates/main_menu.tpl')

<p> <br /> </p>

          % for stream_name in names:
          	{{names[stream_name]}}
	<br />	
          % end