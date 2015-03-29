function Like(id, username){
	$.post("/addLike", {'ideaId' : id, 'username' : username}, function(data){
		$("#likebtn").prop('disabled', true);
		$("#dislikebtn").prop('disabled', false);
		$("#like").text(data);
	});
}

function DisLike(id, username){
	$.post("/disLike", {'ideaId' : id, 'username' : username}, function(data){
		console.log(data);
		$("#dislikebtn").prop('disabled', true);
		$("#likebtn").prop('disabled', false);
		$("#like").text(data);
	});
}

function alreadyLiked(id, username){
	$.get("/userLiked", {'ideaId' : id, 'username' : username}, function(data){
		if (data == "y"){
			$("#likebtn").prop('disabled', true);
			$("#dislikebtn").prop('disabled', false);
		}
	});
}