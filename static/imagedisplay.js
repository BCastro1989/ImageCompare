"use strict";

var main = function() {
    var show_similar_img = function(){
      //Get file to be uploaded
      var formData = new FormData();
      var file = $("input[type='file']")[0].files[0];
      formData.append("file", file);
      //upload file
      $.ajax({
          url : "/uploadimg",
          type : "POST",
          data : formData,
          contentType: false,
          processData: false
      })
      .done(function(image_info){
          // Parse out image info
          var image_info = JSON.parse(image_info);
          var uploaded_img = image_info["Uploaded"]
          var similar_imgs = image_info["Similars"]
          //Tuples representing similar images: (name, similarity)
          var sim_img_1 = similar_imgs[0]
          var sim_img_2 = similar_imgs[1]
          var sim_img_3 = similar_imgs[2]

          //Display Uploaded Image Info
          $("#uploaded-img").attr("src","static/images/"+uploaded_img);
          $("#uploaded-img-name").html(uploaded_img);

          //Display Similar image info
          try{
            $("#similar-img-1").attr("src","static/images/"+sim_img_1[0]);
            $("#similar-img-1-name").text(sim_img_1[0]);
            $("#similar-img-1-percent").text(sim_img_1[1].toString());
            $("#similar-img-2").attr("src","static/images/"+sim_img_2[0]);
            $("#similar-img-2-name").text(sim_img_2[0]);
            $("#similar-img-2-percent").text(sim_img_2[1].toString());
            $("#similar-img-3").attr("src","static/images/"+sim_img_3[0]);
            $("#similar-img-3-name").text(sim_img_3[0]);
            $("#similar-img-3-percent").text(sim_img_3[1].toString());
          }
          catch(e){
            //type error from attempt to get [0] of undefind
            console.log("Less then 3 images to compare. Upload More!");
          }
          //Show similar images container
          $(".similar-imgs").show()
      });
    }

    $("#upload-btn").on("click",function(){
        event.preventDefault();
    	  show_similar_img()
    })
}

$(document).ready(main);
