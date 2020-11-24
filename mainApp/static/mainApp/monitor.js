function delete_rover(rover_id){
    if (confirm("¿Estás seguro de querer eliminar el rover " + rover_id + " y todos sus datos almacenados?")){
        fetch('/api/rover/' + rover_id + '/', {
            method: 'delete'
        }).then();
        window.location.href = "/";

    }
}