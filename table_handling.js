				$('#append_row').on("click", function () {
					$('#list_table').append(
						$('<tr>').append(
							$('<td>').append($('#inUrl').val()),
							$('<td>').append(''),
							$('<td>').append(''),
							$('<td>').append(
								$('<a>').prop('href', '#').addClass('word-analysis').append('단어분석')),
							$('<td>').append(
									$('<a>').prop('href', '#').addClass('similarity-analysis').append('유사도분석'))
						)
					);
				});
				
				$('#list_table').on("click", ".word-analysis", function () {
					var btn = $(this);
					var tr = btn.parent().parent();
					var td = tr.children();
					var Lurl = td.eq(0).text();

					var form = document.createElement('form');
					form.setAttribute('charset', 'UTF-8');
					form.setAttribute('method', 'post');
					form.setAttribute('action', '/urlSending');
					
					var hiddenField = document.createElement('input');
					hiddenField.setAttribute('type', 'hidden');
					hiddenField.setAttribute('name', 'url');
					hiddenField.setAttribute('value', Lurl);
					form.appendChild(hiddenField);
					
					document.body.appendChild(form);
					form.submit();
				});
				
				$('#list_table').on("click", ".similarity-analysis", function () {
					var btn = $(this);
					var tr = btn.parent().parent();
					var td = tr.children();
					var url = td.eq(0).text();
					alert(url);
				});