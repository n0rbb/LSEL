
jQuery(document).ready(function(event){
	var projectsContainer = $('.cd-projects-container'),
		navigation = $('.cd-primary-nav'),
		triggerNav = $('.cd-nav-trigger'),
		logo = $('.cd-logo');
	
	triggerNav.on('click', function(){
		if( triggerNav.hasClass('project-open') ) {
			//close project
			projectsContainer.removeClass('project-open').find('.selected').removeClass('selected').one('webkitTransitionEnd otransitionend oTransitionEnd msTransitionEnd transitionend', function(){
				$(this).children('.cd-project-info').scrollTop(0).removeClass('has-boxshadow');

			});
			triggerNav.add(logo).removeClass('project-open');
		} else {
			//trigger navigation visibility
			triggerNav.add(projectsContainer).add(navigation).toggleClass('nav-open');
		}
	});

	projectsContainer.on('click', '.single-project', function(){
		var selectedProject = $(this);
		if( projectsContainer.hasClass('nav-open') ) {
			//close navigation
			triggerNav.add(projectsContainer).add(navigation).removeClass('nav-open');
		} else {
			//open project
			selectedProject.addClass('selected');
			projectsContainer.add(triggerNav).add(logo).addClass('project-open');

			//AUTO scroll down when clicking on the button
			var visibleProjectContent =  projectsContainer.find('.selected').children('.cd-project-info'),
				windowHeight = $(window).height();

			visibleProjectContent.animate({'scrollTop': windowHeight}, 300); 
		}
	});

	projectsContainer.on('click', '.cd-scroll', function(){
		//scroll down when clicking on the .cd-scroll arrow
		var visibleProjectContent =  projectsContainer.find('.selected').children('.cd-project-info'),
			windowHeight = $(window).height();

		visibleProjectContent.animate({'scrollTop': windowHeight}, 300); 
	});

	//add/remove the .has-boxshadow to the project content while scrolling 
	var scrolling = false;
	projectsContainer.find('.cd-project-info').on('scroll', function(){
		if( !scrolling ) {
		 	(!window.requestAnimationFrame) ? setTimeout(updateProjectContent, 300) : window.requestAnimationFrame(updateProjectContent);
		 	scrolling = true;
		}
	});

	function updateProjectContent() {
		var visibleProject = projectsContainer.find('.selected').children('.cd-project-info'),
			scrollTop = visibleProject.scrollTop();
		( scrollTop > 0 ) ? visibleProject.addClass('has-boxshadow') : visibleProject.removeClass('has-boxshadow');
		scrolling = false;
	}

	
	const reload1 = document.getElementById('reload1');

	reload1.addEventListener('click', function() { // el _ es para indicar la ausencia de parametros
    	location.reload();
    	localStorage.setItem("section", "1");
		//scroll down when clicking on the .cd-scroll arrow
		//var visibleProjectContent =  projectsContainer.find('.selected').children('.cd-project-info'),
		//	windowHeight = $(window).height();

		//visibleProjectContent.animate({'scrollTop': windowHeight}, 300); 
	});

	const reload2 = document.getElementById('reload2');

	reload2.addEventListener('click', _ => { // el _ es para indicar la ausencia de parametros
    	location.reload();
    	localStorage.setItem("section", "2");
	});

	const reload3 = document.getElementById('reload3');

	reload3.addEventListener('click', _ => { // el _ es para indicar la ausencia de parametros
    	location.reload();
    	localStorage.setItem("section", "3");
	});

	$(document).ready(function(){
		if (localStorage.getItem("section") == "1") {
  			$('#1').trigger('click');
		} 
		else if (localStorage.getItem("section") == "2") {
  			$('#2').trigger('click');
		}
		else {
  			$('#3').trigger('click');
		}
	});
});