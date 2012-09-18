/* Copyright 2009-2012 Joey
// 
// Jobot is released under Affero GPL. Please read the license before continuing.
// 
// The latest source can be found here:
//	 https://github.com/MOSW/wallybot
*/

var flist_params = {'from':'factoids','limit':30,'p':1};
var quote_int = null;



	

//pads left
String.prototype.lpad = function(padString, length) {
	var str = this;
    while (str.length < length)
        str = padString + str;
    return str;
	}
 
/*//pads right
String.prototype.rpad = function(padString, length) {
	var str = this;
    while (str.length < length)
        str = str + padString;
    return str;
	}*/





function htmlenc(text){
	return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;');
	}
	
function linkify(text){
	return String(text).replace(/(https?:\/\/[-a-z0-9+&@#\\\/%?=~_()|!:,\.;]*[-a-z0-9+&@#\\\/%=~_()|])/ig, "<a href=\"$1\" target=\"_blank\">$1</a>");
	}
	
	
function compURL(base, params){
	if(!params) return base;
	
	var p = [];
	for(k in params) {
		if(params[k]) p.push(k +'='+ encodeURIComponent(params[k]));
		else p.push(k);
		}
	return base +'?'+ p.join('&');
	}

	
	
function decompURL(url){
	var dict = [], a, x;
	x = url.split('?', 2);
	
	if(!x[1]) return [x[0], {}];
	
	var pairs = x[1].split('&');
	
	for(var i = 0; i < pairs.length; i++){
		a = pairs[i].split('=');
		
		if(!a[1]) dict[a[0]] = '';
		else dict[a[0]] = decodeURIComponent(a[1]);
		}
		
	return [x[0], dict];
	}
	
	
	
function clickNick(event){
	
	flist_params['nick'] = event.target.textContent;
	
	$("#sf #nick")[0].value = event.target.textContent;
	
	updateList();
	
	event.preventDefault();
	}
	
	
	
function clickForget(event){
	var row = $(event.target).parent().hide(300);
	var id = row.find('.id')[0].textContent;
	var type = row.find('.type')[0].textContent;
	
	$.post('ajax/forget', {'id':id}, function(data) {
		act = $.parseJSON(data);
		if(!act['success'] || act['error']){
			row.show(300);
			}
		});
	event.preventDefault();
	}
	
function clickUnforget(event){
	var row = $(event.target).parent().hide(300);
	var id = row.find('.id')[0].textContent;
	//var type = row.find('.type')[0].textContent;
	
	$.post('ajax/unforget', {'id':id}, function(data) {
		//alert('del-response: '+data);
		act = $.parseJSON(data);
		if(!act['success'] || act['error']){
			row.show(300);
			}
		});
	event.preventDefault();
	}
	
	
	
	
function clickEdit(event){
	var row = $(event.target).parent();
	row.addClass('editing');
	
	// yeah yeah, inefficient. I dont really care
	row.find('.find')[0].contentEditable = true;
	row.find('.find').data('orig', row.find('.find')[0].textContent);
	row.find('.inkling')[0].contentEditable = true;
	row.find('.inkling').data('orig', row.find('.inkling')[0].textContent);
	row.find('.verb')[0].contentEditable = true;
	row.find('.verb').data('orig', row.find('.verb')[0].textContent);
	row.find('.reply')[0].contentEditable = true;
	row.find('.reply').data('orig', row.find('.reply')[0].textContent);
	
	event.preventDefault();
	}

	
	
	
function dblclickRow(event){
	var row = $(this);
	
	if(row.hasClass('editing')) return;
	
	row.addClass('editing');
	
	// yeah yeah, inefficient. I dont really care
	row.find('.find')[0].contentEditable = true;
	row.find('.find').data('orig', row.find('.find')[0].textContent);
	row.find('.inkling')[0].contentEditable = true;
	row.find('.inkling').data('orig', row.find('.inkling')[0].textContent);
	row.find('.verb')[0].contentEditable = true;
	row.find('.verb').data('orig', row.find('.verb')[0].textContent);
	row.find('.reply')[0].contentEditable = true;
	row.find('.reply').data('orig', row.find('.reply')[0].textContent);
	
	event.target.focus();
	
	event.preventDefault();
	}
	
	
	
	
function clickCancel(event){
	var row = $(event.target).parent();
	row.removeClass('editing');
	
	// yeah yeah, inefficient. I dont really care
	row.find('.find')[0].contentEditable = false;
	row.find('.find')[0].textContent = row.find('.find').data('orig');
	
	row.find('.inkling')[0].contentEditable = false;
	row.find('.inkling')[0].textContent = row.find('.inkling').data('orig');
	
	row.find('.verb')[0].contentEditable = false;
	row.find('.verb')[0].textContent = row.find('.verb').data('orig');
	
	row.find('.reply')[0].contentEditable = false;
	row.find('.reply')[0].textContent = row.find('.reply').data('orig');
	
	event.preventDefault();
	}
	
	
	

function clickSave(event){
	var row = $(event.target).parent();
	var id = row.find('.id')[0].textContent;
	var type = row.find('.type')[0].textContent;
	row.removeClass('editing');
	
	// yeah yeah, inefficient. I dont really care
	row.find('.find')[0].contentEditable = false;
	var find = row.find('.find')[0].textContent;
	
	row.find('.inkling')[0].contentEditable = false;
	var inkling = row.find('.inkling')[0].textContent;
	
	row.find('.verb')[0].contentEditable = false;
	var verb = row.find('.verb')[0].textContent;
	
	row.find('.reply')[0].contentEditable = false;
	var reply = row.find('.reply')[0].textContent;
	
	$.post('ajax/save', {'id':id, 'type':type, 'find':find, 'inkling':inkling, 'verb':verb, 'reply':reply}, 
	function(data) {
		act = $.parseJSON(data);
		if(!act || !act['success'] || act['error']){
			alert('Error while saving factoid #'+id+': ('+act['error']+')');
			}
		});
	
	event.preventDefault();
	}
	
function rowKeyDown(event){
	if(!$(this).hasClass('editing')) return;
	
	if (event.which == 13) {
		event.preventDefault();
		$(this).find('.save').click();
		event.target.blur();
		}
	}
	
/*<div class="fli %s" id="%s-%d">
	<img src="delete.png" class="delete" />
	<img src="edit.png" class="edit" />
	<img src="undo.png" class="cancel" />
	<img src="save.png" class="save" />
	<span class="type">factoids</span>
	<span class="id">{id}</span><span class="idsep">:</span>
	<span class="find">{find}</span>
	<span class="inklingsep left">(</span>
	<span class="inkling">{inkling}</span>
	<span class="inklingsep right">)</span>
	<span class="verb">{verb}</span>
	<span class="reply">{reply}</span>
	<span class="creator">{creator}</span>
	<span class="lastsaid" title="{fulltime}">{lastsaid}</span>
</div>*/



function listItem(row){
	var fulltime = '';
	var shorttime = '';
	
	if(row[7]){
		var lastsaid = new Date(parseFloat(row[7])*1000);
		fulltime = lastsaid.toString();
		shorttime = lastsaid.getDate()+'/'+(lastsaid.getMonth()+1)+'/'+(lastsaid.getFullYear()-2000)+' '+lastsaid.getHours()+':'+String(lastsaid.getMinutes()).lpad('0',2);
		}
	
	var html = $("<div class=\"fli\">\
	<img src=\"delete.png\" class=\"forget\" title=\"Forget\" />\
	<img src=\"edit.png\" class=\"edit\" title=\"Edit\" />\
	<img src=\"undo.png\" class=\"cancel\" title=\"Cancel\" />\
	<img src=\"save.png\" class=\"save\" title=\"Save\" />\
	<span class=\"type\">factoids</span>\
	<span class=\"id\">"+htmlenc(row[0])+"</span><span class=\"idsep\">:</span>\
	<span class=\"find\">"+linkify(htmlenc(row[2]))+"</span>\
	<span class=\"inklingsep left\">(</span>\
	<span class=\"inkling\">"+htmlenc(row[1])+"</span>\
	<span class=\"inklingsep right\">)</span>\
	<span class=\"verb\">"+htmlenc(row[3])+"</span>\
	<span class=\"reply\">"+linkify(htmlenc(row[4]))+"</span>\
	<span class=\"creator\">"+htmlenc(row[5])+"</span>\
	<span class=\"lastsaid\" title=\""+fulltime+"\">"+shorttime+"</span>\
</div>");
	$('.forget', html).click(clickForget);
	$('.edit', html).click(clickEdit);
	$('.cancel', html).click(clickCancel);
	$('.save', html).click(clickSave);
	$('.creator', html).click(clickNick);
	html.dblclick(dblclickRow);
	html.keydown(rowKeyDown);
	return html;
	}
	
	
// generate deleted row in factoid list
function listItem_d(row){
	var fulltime = '';
	var shorttime = '';
	
	if(row[10]){
		var deltime = new Date(parseFloat(row[10])*1000);
		fulltime = deltime.toString();
		shorttime = deltime.getDate()+'/'+(deltime.getMonth()+1)+'/'+(deltime.getFullYear()-2000)+' '+deltime.getHours()+':'+String(deltime.getMinutes()).lpad('0',2);
		}
	
	var html = $("<div class=\"fli\">\
	<img src=\"arrow_medium_left.png\" class=\"unforget\" title=\"Unforget\" />\
	<img src=\"edit.png\" class=\"edit\" title=\"Edit\" />\
	<img src=\"undo.png\" class=\"cancel\" title=\"Cancel\" />\
	<img src=\"save.png\" class=\"save\" title=\"Save\" />\
	<span class=\"type\">del_factoids</span>\
	<span class=\"id\">"+htmlenc(row[0])+"</span><span class=\"idsep\">:</span>\
	<span class=\"find\">"+linkify(htmlenc(row[2]))+"</span>\
	<span class=\"inklingsep left\">(</span>\
	<span class=\"inkling\">"+htmlenc(row[1])+"</span>\
	<span class=\"inklingsep right\">)</span>\
	<span class=\"verb\">"+htmlenc(row[3])+"</span>\
	<span class=\"reply\">"+linkify(htmlenc(row[4]))+"</span>\
	<span class=\"creator d\">"+htmlenc(row[5])+"</span>\
	<span class=\"deleter\" title=\"Deleted by: "+htmlenc(row[11])+"!"+htmlenc(row[12])+"@"+htmlenc(row[13])+" from "+htmlenc(row[14])+"\">"+htmlenc(row[11])+"</span>\
	<span class=\"lastsaid\" title=\""+fulltime+"\">"+shorttime+"</span>\
</div>");
	$('.unforget', html).click(clickUnforget);
	$('.edit', html).click(clickEdit);
	$('.cancel', html).click(clickCancel);
	$('.save', html).click(clickSave);
	$('.creator', html).click(clickNick);
	html.dblclick(dblclickRow);
	html.keydown(rowKeyDown);
	return html;
	}
	

	
function updateList_h(data){
	if(data['error']){
		alert('Unable to update list. Error: '+data['error']);
		return
		}
		
	var flist = $(".flist").html('');
	
	
	if(!data.rows.length){
		flist.html('<h2>0 Results</h2>');
		return
		}
	
	
	
	var offset = (flist_params['p']?flist_params['p']-1:0)*flist_params['limit'];
	
	$('.showing').text('Showing '+(offset+1)+'-'+(offset + data.rows.length)+' of '+data.count);
	
	var totalpages = Math.ceil(data.count/flist_params['limit']);
	if(flist_params['p'] >= totalpages)
		$('.page_control .next').hide();
	else
		$('.page_control .next').show();
		
	if(flist_params['p'] <= 1)
		$('.page_control .prev').hide();
	else
		$('.page_control .prev').show();
	
	
	var b = false;
	var itemFunc = (data.from=='del_factoids')?listItem_d:listItem;
	
	for(r in data.rows){
		b = !b;
		flist.append(itemFunc(data.rows[r]).addClass(b?'fli1':'fli2'))
		}
	
	flist.scrollTop(0);
	}

	
	
function updateList(){
	$.getJSON(compURL('ajax/list', flist_params), updateList_h);
	}
	
	
	
	
	
	
	
	
function updateUserlist(){
	$.getJSON(compURL('ajax/userlist'), updateUserlist_h);
	}
	
function updateUserlist_h(data){
	if(data.error){
		alert('Unable to fetch user list. Error: '+data.error);
		return
		}
		
	ulist = $('.userlist').html('<div class="uli"><span class="id" style="margin-left:51px;">ID</span><span class="user">User</span><span class="nick">Nick</span><span class="ident">Ident</span><span class="host">Host</span><span class="level">Level</span></div>');
	
	if(!data.users.length){
		flist.html('<h2>0 Users</h2>');
		return
		}
		
	var b = true;
	for(u in data.users){
		b = !b;
		ulist.append(ulistrow(data.users[u]).addClass(b?'fli1':'fli2'))
		}
	
	}
	
function ulistrow(row){
	var html = $("<div class=\"uli\"><img src=\"delete.png\" class=\"delete\" title=\"Forget\" />\
	<img src=\"edit.png\" class=\"edit\" title=\"Edit\" />\
	<span class=\"id\">"+htmlenc(row[0])+"</span>\
	<span class=\"user\">"+htmlenc(row[1])+"</span>\
	<span class=\"nick\">"+htmlenc(row[2]?row[2]:' ')+"</span>\
	<span class=\"ident\">"+htmlenc(row[3]?row[3]:' ')+"</span>\
	<span class=\"host\">"+htmlenc(row[4]?row[4]:' ')+"</span>\
	<span class=\"level\">"+htmlenc(row[5]?row[5]:' ')+"</span>\
	<a class=\"save\" href=\"#save\">Save</a> \
	<input type=\"text\" class=\"user\" placeholder=\"User\" style=\"width:80px;\" value=\""+htmlenc(row[1])+"\" /> \
	<input type=\"text\" class=\"pass\" placeholder=\"Password\" /> \
	<input type=\"text\" class=\"nick\" placeholder=\"Nick\" style=\"width:70px;\" value=\""+htmlenc(row[2])+"\" /> \
	<input type=\"text\" class=\"ident\" placeholder=\"Ident\" value=\""+htmlenc(row[3])+"\" /> \
	<input type=\"text\" class=\"host\" placeholder=\"Host\" style=\"width:160px;\" value=\""+htmlenc(row[4])+"\" /> \
	<input type=\"text\" class=\"level\" placeholder=\"Level\" value=\""+htmlenc(row[5])+"\" />\
	</div>");
	
	
	
	$('.edit', html).click(function(event){
		$(this).parent().find('.edit,.delete,.save,.id,.user,.pass,.nick,.ident,.host,.level').slideToggle()
		event.preventDefault();
		});
		
		
	$('.delete', html).click(function(event){
		var id = $(this).parent().find('.id').text();
		$.post('ajax/deluser', { 'id':id}, 
			function(data) {
				act = $.parseJSON(data);
				if(!act || !act['success'] || act['error']){
					alert('Error while deleting user #'+id+': ('+act['error']+')');
					}
				updateUserlist();
				});
		
		event.preventDefault();
		});
		
	$('.save', html).click(function(event){
		var id = $(this).parent().find('span.id').text();
		var user = $(this).parent().find('input.user').val();
		var pass = $(this).parent().find('input.pass').val();
		var nick = $(this).parent().find('input.nick').val();
		var ident = $(this).parent().find('input.ident').val();
		var host = $(this).parent().find('input.host').val();
		var level = $(this).parent().find('input.level').val();
		$.post('ajax/saveuser', { 'id':id, 'user':user, 'pass':pass, 'nick':nick, 'ident':ident, 'host':host, 'level':level }, 
			function(data) {
				act = $.parseJSON(data);
				if(!act || !act['success'] || act['error']){
					alert('Error while saving user #'+id+': ('+act['error']+')');
					}
				updateUserlist();
				});
		
		event.preventDefault();
		});
		
	return html;
	}
	
	
	
	
function updateQuote(){
	$.getJSON('ajax/quote', function(data){
		if(data && data[0] && !data['error']){
			$('.wbub').attr('title',data[0]+' by '+data[1]).html(linkify(data[2]))
			}
		});
	}
	
	
function updateStats(){
	$.getJSON('ajax/stats', function(data){
		if(data && data['factoids']){
			$('.tab .factoids.c').text(data['factoids']);
			}
		if(data && data['del_factoids']){
			$('.tab .del_factoids.c').text(data['del_factoids']);
			}
		});
	}
	
	
$(document).ready(function(){
	
	
	if($('.flist').length){
		updateQuote();
		updateList();
		updateStats();
		}
	
	
	// sorting links
	$(".sort a").click(function(event){
		
		flist_params['by'] = event.target.title;
		
		updateList();
		
		$(".sort a.active").removeClass('active');
		$(event.target).addClass('active');
		
		event.preventDefault();
		});
		
	
	// search box sumbit
	$("#sf").submit(function(event){
		
		flist_params['nick'] = $("#sf #nick")[0].value;
		flist_params['s'] = $("#sf #search")[0].value;
		flist_params['id'] = $("#sf #id")[0].value;
		flist_params['deleter'] = $("#sf #deleter")[0].value;
		flist_params['exactnick'] = $("#sf #exactnick")[0].checked;
		flist_params['sfind'] = $("#sf #sfind")[0].checked;
		flist_params['sreply'] = $("#sf #sreply")[0].checked;
		if(flist_params['p']) delete flist_params['p'];
		
		updateList();
		
		event.preventDefault();
		});
		
		
		
	// search box reset
	$('#sf input[type="reset"]').click(function(event){
		
		if('nick' in flist_params) delete flist_params['nick'];
		if('s' in flist_params) delete flist_params['s'];
		if('p' in flist_params) delete flist_params['p'];
		if('id' in flist_params) delete flist_params['id'];
		if('deleter' in flist_params) delete flist_params['deleter'];
		if('exactnick' in flist_params) delete flist_params['exactnick'];
		if('sfind' in flist_params) delete flist_params['sfind'];
		if('sreply' in flist_params) delete flist_params['sreply'];
		
		$("#sf #nick")[0].value = '';
		$("#sf #search")[0].value = '';
		$("#sf #deleter")[0].value = '';
		$("#sf #exactnick")[0].checked = true;
		$("#sf #sfind")[0].checked = true;
		$("#sf #sreply")[0].checked = true;
		
		updateList();
		
		event.preventDefault();
		});
	
	$('#sf .more').click(function(event){
		$('#sf .extra').slideToggle(200);
		});
	
	
	// Factoid and Deleted Tabs
	$(".tlinks .tab").click(function(event){
		
		flist_params['from'] = this.title;
		
		// goto page 1
		delete flist_params['p'];
		
		updateList();
		event.preventDefault();
		});
	
	$('.page_control .next').click(function(event){
		if('p' in flist_params)
			flist_params['p'] += 1;
		else
			flist_params['p'] = 2;
		
		updateList();
		event.preventDefault();
		});
		
	$('.page_control .prev').click(function(event){
		if('p' in flist_params)
			flist_params['p'] -= 1;
		
		updateList();
		event.preventDefault();
		});
	
	$('.wbub, .it, .wbub1, .wbub2, .wbub3').click(function(event){
		updateQuote();
		event.preventDefault();
		});
	
	$('.sett_links .users').click(function(event){
		if($('.userlistw').is(':hidden')){
			updateUserlist();
			$('.flist, .showing, .page_control').slideUp();
			$('.userlistw').fadeIn();
		}else{
			$('.flist, .showing, .page_control').slideDown();
			$('.userlistw').fadeOut();
			}
		event.preventDefault();
		});
		
	/*$('.sett_links .settings').click(function(event){
		$('.flist, .showing, .page_control').slideUp();
		
		event.preventDefault();
		});*/
		
	
	$('.userlistw .adduserlnk').click(function(event){
		$('.userlistw .adduserform input').val('')
		$('.userlistw .adduserform').toggle(500,'swing');
		
		if(this.textContent != 'Cancel'){
			this.textContent = 'Cancel';
			$('.adduserform .user')[0].focus()
		}else{
			this.textContent = '+ Add User';
			}
			
		event.preventDefault();
		});
		
		
	$('.userlistw .createuser').click(function(event){
		var user = $('.adduserform .user').val();
		var pass = $('.adduserform .pass').val();
		var level = $('.adduserform .level').val();
		
		$.post('ajax/newuser', { 'user':user, 'pass':pass, 'level':level}, 
			function(data) {
				act = $.parseJSON(data);
				if(!act || !act['success'] || act['error']){
					alert('Error while creating user: ('+act['error']+')');
					}
				updateUserlist();
				});
		$('.userlistw .adduserlnk').click();
		event.preventDefault();
		});
	});