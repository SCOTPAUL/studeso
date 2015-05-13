/**
 * Created by paul on 17/03/15.
 */

$(document).ready(function(){
    var taggle = new Taggle('tags', {
        placeholder: 'Press return to add tag...',
        duplicateTagClass: 'bounce',
        tabIndex: 5,

        onTagAdd: function(event, tag){
            if(tag.length > 30){
                taggle.remove(tag);
            }
            else if(tag.slice(-5) == "ac.uk"){
                $.get(
                    '/inst_tag_valid/',
                    {tag_name: tag},
                    function(data){
                        if(data['valid']){
                            $('.taggle_text:contains('+tag+')')
                                .parent().attr('id', 'inst_tag');
                        }
                        else {
                            taggle.remove(tag);
                        }
                    },
                    "json");
            }
        }
    });
});
