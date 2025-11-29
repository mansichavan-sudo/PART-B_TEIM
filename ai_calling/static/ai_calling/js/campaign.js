// campaign.js
// Frontend behaviour for AI-calling campaign pages
$(function() {
  // CSRF setup for AJAX (Django)
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i=0;i<cookies.length;i++) {
        const c = cookies[i].trim();
        if (c.substring(0, name.length+1) === (name + "=")) {
          cookieValue = decodeURIComponent(c.substring(name.length+1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');
  $.ajaxSetup({
    headers: { "X-CSRFToken": csrftoken },
    contentType: "application/json"
  });

  // Utility: show alerts
  function showMessage(selector, html, type='success') {
    const el = $(selector);
    el.html(`<div class="alert alert-${type}">${html}</div>`);
    setTimeout(()=>el.html(''), 5000);
  }

  // Load templates into template select
  function loadTemplates() {
    $.get("/api/ai-calling/templates/").done(function(resp) {
      const sel = $("#template");
      sel.empty().append('<option value="">-- Select template --</option>');
      if (!resp || resp.length===0) return;
      resp.forEach(t=>{
        sel.append(`<option value="${t.id}">${t.template_name} (${t.language})</option>`);
      });
    }).fail(()=>{ /* ignore */ });
  }

  // Campaign list page: populate table
  function loadCampaigns() {
    if ($("#campaignTable").length===0) return;
    $.get("/api/ai-calling/campaigns/").done(function(resp) {
      const tb = $("#campaignTable tbody").empty();
      resp.forEach(c=>{
        const schedule = c.schedule_type === 'immediate' ? 'Immediate' : (c.schedule_date ? `${c.schedule_date} ${c.schedule_time||''}` : c.schedule_type);
        tb.append(`
          <tr>
            <td>${c.name}</td>
            <td>${c.lead_type}</td>
            <td>${c.service_type}</td>
            <td>${c.language}</td>
            <td>${schedule}</td>
            <td>${c.recommendation_enabled ? 'Yes' : 'No'}</td>
            <td>
              <a class="btn btn-sm btn-outline-primary me-1" href="/ai-calling/campaigns/${c.id}/edit/">Edit</a>
              <button class="btn btn-sm btn-danger btn-delete" data-id="${c.id}">Delete</button>
              <button class="btn btn-sm btn-success btn-run" data-id="${c.id}">Run</button>
            </td>
          </tr>
        `);
      });
    }).fail(()=>showMessage('#campaignAlert','Could not load campaigns','danger'));
  }

  // Delete
  $(document).on('click','.btn-delete', function(){
    if (!confirm('Delete this campaign?')) return;
    const id = $(this).data('id');
    $.ajax({
      url: `/api/ai-calling/campaigns/${id}/`,
      type: 'DELETE'
    }).done(()=>{ showMessage('#campaignAlert','Deleted'); loadCampaigns(); })
    .fail(()=>showMessage('#campaignAlert','Delete failed','danger'));
  });

  // Run campaign (trigger)
  $(document).on('click','.btn-run', function(){
    const id = $(this).data('id');
    $(this).prop('disabled', true).text('Running...');
    $.post(`/api/ai-calling/campaigns/${id}/run/`, JSON.stringify({}))
      .done(()=> showMessage('#campaignAlert','Campaign triggered'))
      .fail(()=> showMessage('#campaignAlert','Trigger failed','danger'))
      .always(()=> { $(this).prop('disabled', false).text('Run'); });
  });

  // Show / hide schedule fields
  $('#schedule_type').on('change', function(){
    const v = $(this).val();
    if (v === 'scheduled' || v === 'recurring') $('.schedule-fields').removeClass('d-none');
    else $('.schedule-fields').addClass('d-none');
  });

  // Toggle recommendation block
  $('#recommendation_enabled').on('change', function(){
    if ($(this).is(':checked')) $('#recommendationBlock').removeClass('d-none');
    else $('#recommendationBlock').addClass('d-none');
  });

  // Save campaign (form submit)
  $('#campaignForm').on('submit', function(e){
    e.preventDefault();
    const id = $('#campaignId').val();
    const url = id ? `/api/ai-calling/campaigns/${id}/` : '/api/ai-calling/campaigns/';
    const method = id ? 'PUT' : 'POST';

    // collect data
    const data = {
      name: $('#name').val(),
      description: $('#description').val(),
      lead_type: $('#lead_type').val(),
      service_type: $('#service_type').val(),
      language: $('#language').val(),
      caller_id: $('#caller_id').val(),
      template: $('#template').val(),
      retry_attempts: parseInt($('#retry_attempts').val()||0),
      schedule_type: $('#schedule_type').val(),
      schedule_date: $('#schedule_date').val(),
      schedule_time: $('#schedule_time').val(),
      recommendation_enabled: $('#recommendation_enabled').is(':checked'),
      upsell_text: $('#upsell_text').val(),
      crosssell_text: $('#crosssell_text').val(),
      fallback_whatsapp: $('#fallback_whatsapp').is(':checked'),
      fallback_email: $('#fallback_email').is(':checked'),
      fallback_voicemail: $('#fallback_voicemail').is(':checked')
    };

    $.ajax({
      url: url,
      type: method,
      data: JSON.stringify(data)
    }).done(function(resp){
      showMessage('#formMessage','Saved successfully','success');
      // redirect to list after save
      window.location.href = '/ai-calling/';
    }).fail(function(xhr){
      const err = xhr.responseJSON && xhr.responseJSON.detail ? xhr.responseJSON.detail : 'Save failed';
      showMessage('#formMessage', err, 'danger');
    });
  });

  // Test call
  $('#testCallBtn').on('click', function(){
    const number = $('#test_number').val().trim();
    const template = $('#template').val();
    if (!number) { alert('Enter test number'); return; }
    $(this).prop('disabled', true).text('Sending...');
    $.post('/api/ai-calling/test-call/', JSON.stringify({ phone: number, template_id: template }))
      .done(()=> showMessage('#formMessage','Test call initiated','success'))
      .fail(()=> showMessage('#formMessage','Test call failed','danger'))
      .always(()=> $(this).prop('disabled', false).text('Place Test Call'));
  });

  // On campaign create/edit page load: fill template select
  loadTemplates();

  // On list page load: populate campaigns
  loadCampaigns();
});
