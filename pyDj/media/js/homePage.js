var xmlhttp;
var ckBoxesSelected;
var ckBoxes;

function ajaxCall(url,cfunc){
    if (window.XMLHttpRequest){xmlhttp=new XMLHttpRequest();  }
    else  {xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");  }
    xmlhttp.onreadystatechange=cfunc;
    xmlhttp.open("GET",url,true);
    xmlhttp.send();
}

function init(){
    leftSideBar();
    //setInterval(function(){leftSideBar()},30000);
}

function leftSideBar(){ajaxCall("/leftSideBar/",function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
    resp=JSON.parse(xmlhttp.responseText);
    document.getElementById("leftSideBar").innerHTML=resp.innerHTML;
}})}

function mainPage(x){
    if (x==''){ x='Unorganized'}
    ajaxCall("/mainPage/?album="+x,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
        resp=JSON.parse(xmlhttp.responseText);
        document.getElementById("mainPage").innerHTML=resp.innerHTML;
        ckBoxes=resp.ckBoxes;
        ckBoxesSelected=new Array() ;
    }})}

function createAlbum(){
    var x=prompt("Enter the name for New Album","");
    if (x!=null && x!=""){
        ajaxCall("/createAlbum/?album="+x,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            resp=JSON.parse(xmlhttp.responseText);
            leftSideBar();
        }})}}

function renameAlbum(x){
    var y=prompt("Enter the new Name for the Album",x);
    if (y!=null && y!=""){
        ajaxCall("/renameAlbum/?album="+x+"&newName="+y,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            resp=JSON.parse(xmlhttp.responseText);
            leftSideBar();
            mainPage(y);
        }})}}

function deleteAlbum(x){
    var r=confirm("Do you really want to delete the album?");
    if (r==true){
        ajaxCall("/deleteAlbum/?album="+x,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            resp=JSON.parse(xmlhttp.responseText);
            document.getElementById("mainPage").innerHTML=resp.innerHTML;
            leftSideBar();
        }})}}

function loadImage(x){
    //var r=confirm("Would you like to see this image?");
    //if (r==true){
    ajaxCall("/loadImage/?image="+x,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
        resp=JSON.parse(xmlhttp.responseText);
        document.getElementById("Image").innerHTML=resp.innerHTML;
        document.getElementById("Image").focus();
    }})}//}

function modifySelect(x){
    if(document.getElementById(x).checked)
        ckBoxesSelected.push(x);
    else
        ckBoxesSelected.splice(ckBoxesSelected.indexOf(x),1);
    //alert(ckBoxesSelected);
}

function selectAll(){
    ckBoxesSelected=ckBoxes;
    for(i in ckBoxes)
        document.getElementById(ckBoxes[i]).checked=true;
}

function unSelectAll(){
    ckBoxesSelected=new Array();
    for(i in ckBoxes)
        document.getElementById(ckBoxes[i]).checked=false;
}

function deletePhotos(){
    var r=confirm("Do you really wanna to delete these photos?");
    if ((r==true)&&(ckBoxesSelected.length>0)){
        x='';
        for(i=0;i<ckBoxesSelected.length;i++){
            if(i>0)
                x=x+'||';
            x=x+ckBoxesSelected[i];
        }
        ajaxCall("/deletePhotos/?data="+x,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            resp=JSON.parse(xmlhttp.responseText);
            document.getElementById("mainPage").innerHTML=resp.innerHTML;
            leftSideBar();
        }})}}

function downloadPhotos(){
    var r=confirm("Do you want to download these photos?");
    if ((r==true)&&(ckBoxesSelected.length>0)){
        x='';
        for(i=0;i<ckBoxesSelected.length;i++){
            if(i>0)
                x=x+'||';
            x=x+ckBoxesSelected[i];
        }
        ajaxCall("/downloadPhotos/?data="+x,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            resp=JSON.parse(xmlhttp.responseText);
            window.open(resp.path,'download');
        }})}}

function movePhotos(){
    var y=prompt("Enter the name of the Album, you want the photos moved to",'Unorganized');
    if (((y!=null && y!=""))&&(ckBoxesSelected.length>0)){
        x='';
        for(i=0;i<ckBoxesSelected.length;i++){
            if(i>0)
                x=x+'||';
            x=x+ckBoxesSelected[i];
        }
        ajaxCall("/movePhotos/?data="+x+"&album="+y,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            resp=JSON.parse(xmlhttp.responseText);
            document.getElementById("mainPage").innerHTML=resp.innerHTML;
            leftSideBar();
        }})}}

function logout(){ajaxCall("/logout/",function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
    resp=JSON.parse(xmlhttp.responseText);
    document.getElementById("all").innerHTML=resp.innerHTML;
}})}

function makeCollage(){
    var r=confirm("Do you really want to make Collage?");
    if ((r==true)&&(ckBoxesSelected.length>0)){
        x='';
        for(i=0;i<ckBoxesSelected.length;i++){
            if(i>0)
                x=x+'||';
            x=x+ckBoxesSelected[i];
        }
        ajaxCall("/makeCollage/?data="+x,function(){if (xmlhttp.readyState==4 && xmlhttp.status==200) {
            setTimeout(function(){
            resp=JSON.parse(xmlhttp.responseText);
            document.getElementById("Image").innerHTML=resp.innerHTML;
            window.open(resp.path,'download');

            },5000);
        }})}}
