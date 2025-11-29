// template.js - manage templates page
$(function(){
  function getCookie(name){
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let c of cookies) {
        c = c.trim();
        if (c.startsWith(name + '=')) {
          cookieValue = decodeURIComponent(c.substring(name.length+1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');
  $.ajaxSetup({ headers: { "X-CSRFToken": csrftoken }, contentType: "application/json" });

  function renderList(items){
    const container = $('#templatesList').empty();
    if (!items || items.length===0) return container.html('<p class="text-muted">No templates yet.</p>');
    items.forEach(t=>{
      container.append(`
        <div class="card mb-2">
          <div class="card-body">
            <div class="d-flex justify-content-between">
              <div>
                <strong>${t.template_name}</strong> <span class="text-muted">(${t.language})</span>
                <div class="small mt-2">${t.voice_script.substring(0,200)}${t.voice_script.length>200?'...':''}</div>
              </div>
              <div>
                <a href="#" class="btn btn-sm btn-primary btn-edit" data-id="${t.id}">Edit</a>
                <button class="btn btn-sm btn-danger btn-delete" data-id="${t.id}">Delete</button>
              </div>
            </div>
          </div>
        </div>
      `);
    });
  }

  // load templates
  function load(){
    $.get('/api/ai-calling/templates/').done(renderList);
  }

  load();

  // save template
  $('#templateForm').on('submit', function(e){
    e.preventDefault();
    const id = $('#templateId').val();
    const url = id ? `/api/ai-calling/templates/${id}/` : '/api/ai-calling/templates/';
    const method = id ? 'PUT' : 'POST';
    const data = {
      template_name: $('#template_name').val(),
      language: $('#template_language').val(),
      tts_voice: $('#tts_voice').val(),
      voice_script: $('#voice_script').val()
    };
    $.ajax({ url, type: method, data: JSON.stringify(data) })
      .done(()=> { showTempMsg('Saved'); $('#templateForm')[0].reset(); load(); })
      .fail(()=> showTempMsg('Failed to save','danger'));
  });

  function showTempMsg(msg, type='success'){
    $('#templateForm').prepend(`<div class="alert alert-${type}">${msg}</div>`);
    setTimeout(()=> $('#templateForm .alert').remove(),4000);
  }

  // delete template
  $(document).on('click','.btn-delete', function(){
    if (!confirm('Delete template?')) return;
    const id = $(this).data('id');
    $.ajax({ url: `/api/ai-calling/templates/${id}/`, type: 'DELETE' })
      .done(()=> load())
      .fail(()=> showTempMsg('Delete failed','danger'));
  });

  // edit (load into form)
  $(document).on('click','.btn-edit', function(e){
    e.preventDefault();
    const id = $(this).data('id');
    $.get(`/api/ai-calling/templates/${id}/`).done(function(t){
      $('#templateId').val(t.id);
      $('#template_name').val(t.template_name);
      $('#template_language').val(t.language);
      $('#tts_voice').val(t.tts_voice);
      $('#voice_script').val(t.voice_script);
      window.scrollTo({top:0, behavior:'smooth'});
    });
  });
});
