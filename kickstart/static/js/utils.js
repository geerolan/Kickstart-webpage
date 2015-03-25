function Like(id, username){
	$.post("/addLike", {'ideaId' : id, 'username' : username}, function(data){
		console.log(data);
		$("#like").text(data);
	});
}

function DisLike(id, username){
	$.post("/disLike", {'ideaId' : id, 'username' : username}, function(data){
		console.log(data);
		$("#like").text(data);
	});
}
