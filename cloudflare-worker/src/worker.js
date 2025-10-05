// Job Scraper Cloudflare Worker
// Handles job submissions and provides APIs for job data

// CORS headers for API responses
const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type',
};

// Daily scheduled handler - runs every 24 hours
async function handleScheduled(event, env, ctx) {
  console.log('🕰️ Scheduled job triggered:', event.cron);
  
  try {
    // 1. Trigger daily scraping job
    await triggerDailyScraping(env);
    
    // 2. Export data to R2 for Spark processing
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const dateStr = yesterday.toISOString().split('T')[0];
    await exportDataToR2(env, dateStr);
    
    console.log('✅ Daily scheduled tasks completed');
  } catch (error) {
    console.error('❌ Error in scheduled handler:', error);
    throw error;
  }
}

// Trigger daily scraping job (placeholder - actual scraping happens externally)
async function triggerDailyScraping(env) {
  console.log('🚀 Triggering daily scraping job...');
  
  // Options for implementation:
  // 1. Call GitHub Actions workflow API to trigger scraping
  // 2. Use a separate compute service (like Google Cloud Functions)
  // 3. Send webhook to external service
  
  // For now, we'll log a scraping job to track when it was triggered
  const jobId = crypto.randomUUID();
  const result = await env.DB.prepare(`
    INSERT INTO scraping_jobs (job_id, source, status, started_at)
    VALUES (?, 'daily_scheduled', 'triggered', ?)
  `).bind(jobId, new Date().toISOString()).run();
  
  console.log(`✅ Scraping job logged with ID: ${jobId}`);
  return jobId;
}

// Export data to R2 for Spark processing
async function exportDataToR2(env, exportDate) {
  console.log('📦 Exporting recent data to R2...');
  
  // Check if R2 is available
  if (!env.BUCKET) {
    console.log('⚠️ R2 bucket not available - storing export metadata in D1');
    
    // Get the data that would be exported
    const jobs = await env.DB.prepare(`
      SELECT * FROM jobs 
      WHERE DATE(created_at) = ? 
      ORDER BY created_at DESC
    `).bind(exportDate).all();
    
    if (jobs.results.length === 0) {
      console.log(`📭 No jobs found for ${exportDate}`);
      return;
    }
    
    // Store export metadata in D1 (without actual file)
    await env.DB.prepare(`
      INSERT INTO data_exports (date, file_path, job_count, exported_at, status)
      VALUES (?, ?, ?, ?, ?)
    `).bind(
      exportDate,
      `r2://job-data-bucket/exports/${exportDate}.json`,
      jobs.results.length,
      new Date().toISOString(),
      'pending_r2_setup'
    ).run();
    
    console.log(`📋 Export metadata stored for ${jobs.results.length} jobs on ${exportDate}`);
    return;
  }
  
  try {
    // Get jobs from the specified date
    const jobs = await env.DB.prepare(`
      SELECT * FROM jobs 
      WHERE DATE(created_at) = ? 
      ORDER BY created_at DESC
    `).bind(exportDate).all();
    
    if (jobs.results.length === 0) {
      console.log(`📭 No jobs found for ${exportDate}`);
      return;
    }
    
    // Prepare data for export
    const exportData = {
      export_date: exportDate,
      exported_at: new Date().toISOString(),
      job_count: jobs.results.length,
      jobs: jobs.results
    };
    
    // Upload to R2
    const fileName = `exports/${exportDate}.json`;
    await env.BUCKET.put(fileName, JSON.stringify(exportData, null, 2), {
      httpMetadata: {
        contentType: 'application/json',
      },
    });
    
    // Log export in database
    await env.DB.prepare(`
      INSERT INTO data_exports (date, file_path, job_count, exported_at, status)
      VALUES (?, ?, ?, ?, ?)
    `).bind(
      exportDate,
      `r2://job-data-bucket/${fileName}`,
      jobs.results.length,
      new Date().toISOString(),
      'completed'
    ).run();
    
    console.log(`✅ Exported ${jobs.results.length} jobs to R2: ${fileName}`);
    
  } catch (error) {
    console.error('❌ Error exporting to R2:', error);
    
    // Log failed export
    await env.DB.prepare(`
      INSERT INTO data_exports (date, file_path, job_count, exported_at, status, error_message)
      VALUES (?, ?, ?, ?, ?, ?)
    `).bind(
      exportDate,
      `r2://job-data-bucket/exports/${exportDate}.json`,
      0,
      new Date().toISOString(),
      'failed',
      error.message
    ).run();
    
    throw error;
  }
}

// Main request handler
async function handleRequest(request, env, ctx) {
  const url = new URL(request.url);
  const path = url.pathname;

  // Handle CORS preflight requests
  if (request.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  // Route requests based on path
  try {
    if (path === '/api/jobs' && request.method === 'POST') {
      return await handleJobSubmission(request, env, corsHeaders);
    }
    
    if (path === '/api/jobs' && request.method === 'GET') {
      return await handleGetJobs(request, env, corsHeaders);
    }
    
    if (path === '/api/stats' && request.method === 'GET') {
      return await handleGetStats(request, env, corsHeaders);
    }
    
    if (path === '/api/export' && request.method === 'POST') {
      return await handleManualExport(request, env, corsHeaders);
    }
    
    if (path === '/api/scraping-jobs' && request.method === 'GET') {
      return await handleGetScrapingJobs(request, env, corsHeaders);
    }
    
    if (path === '/api/trigger-scrape' && request.method === 'POST') {
      return await handleTriggerScrape(request, env, corsHeaders);
    }
    
    // Default response with API documentation
    return new Response(`
<!DOCTYPE html>
<html>
<head>
    <title>Job Scraper API</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        .endpoint { background: #f5f5f5; padding: 15px; margin: 10px 0; border-radius: 5px; }
        .method { color: #007acc; font-weight: bold; }
        code { background: #eee; padding: 2px 5px; border-radius: 3px; }
    </style>
</head>
<body>
    <h1>🔍 Job Scraper API</h1>
    <p>Welcome to the Job Scraper API. This service collects and stores job postings from various sources.</p>
    
    <h2>📋 Available Endpoints</h2>
    
    <div class="endpoint">
        <h3><span class="method">POST</span> /api/jobs</h3>
        <p>Submit a new job posting</p>
        <code>{ "title": "Software Engineer", "company": "TechCorp", "location": "Remote", "url": "...", "source": "yc" }</code>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/jobs</h3>
        <p>Retrieve job postings with optional filters</p>
        <code>?source=yc&limit=10&offset=0&company=TechCorp</code>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/stats</h3>
        <p>Get database statistics and job counts</p>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">POST</span> /api/export</h3>
        <p>Manually trigger data export to R2</p>
        <code>{ "date": "2025-10-02" }</code>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">GET</span> /api/scraping-jobs</h3>
        <p>Get recent scraping job history</p>
    </div>
    
    <div class="endpoint">
        <h3><span class="method">POST</span> /api/trigger-scrape</h3>
        <p>Manually trigger a scraping job</p>
        <code>{ "source": "yc", "max_jobs": 100 }</code>
    </div>
    
    <p><em>Generated by Cloudflare Worker - Job Scraper API</em></p>
</body>
</html>
    `, {
      headers: { ...corsHeaders, 'Content-Type': 'text/html' }
    });
    
  } catch (error) {
    console.error('Error handling request:', error);
    return new Response(JSON.stringify({ 
      error: 'Internal server error',
      message: error.message 
    }), { 
      status: 500, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// Handle job submission
async function handleJobSubmission(request, env, corsHeaders) {
  try {
    const job = await request.json();
    
    // Validate required fields
    if (!job.title || !job.url || !job.source) {
      return new Response(JSON.stringify({ 
        error: 'Missing required fields: title, url, source' 
      }), { 
        status: 400, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Insert job into database with enhanced fields
    const result = await env.DB.prepare(`
      INSERT INTO jobs (
        title, company, location, url, description_text, description_html, 
        salary, job_type, experience_level, source, scraped_at, created_at
      )
      VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    `).bind(
      job.title,
      job.company || null,
      job.location || null,
      job.url,
      job.description_text || job.description || null,  // Support both field names
      job.description_html || null,
      job.salary || null,
      job.job_type || null,
      job.experience_level || null,
      job.source,
      job.scraped_at || new Date().toISOString(),
      new Date().toISOString()
    ).run();

    console.log('Enhanced job inserted:', result);

    return new Response(JSON.stringify({ 
      success: true, 
      id: result.meta.last_row_id,
      message: 'Job submitted successfully',
      fields: {
        title: job.title,
        company: job.company || 'N/A',
        location: job.location || 'N/A',
        salary: job.salary || 'N/A',
        job_type: job.job_type || 'N/A'
      }
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    console.error('Error submitting job:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to submit job',
      message: error.message,
      details: error.toString()
    }), { 
      status: 500, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// Handle getting jobs with filters
async function handleGetJobs(request, env, corsHeaders) {
  try {
    const url = new URL(request.url);
    const source = url.searchParams.get('source');
    const company = url.searchParams.get('company');
    const limit = parseInt(url.searchParams.get('limit')) || 50;
    const offset = parseInt(url.searchParams.get('offset')) || 0;

    let query = 'SELECT * FROM jobs WHERE 1=1';
    const params = [];

    if (source) {
      query += ' AND source = ?';
      params.push(source);
    }

    if (company) {
      query += ' AND company LIKE ?';
      params.push(`%${company}%`);
    }

    query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?';
    params.push(limit, offset);

    const result = await env.DB.prepare(query).bind(...params).all();
    
    return new Response(JSON.stringify({
      jobs: result.results,
      count: result.results.length,
      limit,
      offset
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error fetching jobs:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to fetch jobs',
      message: error.message 
    }), { 
      status: 500, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// Handle getting database stats
async function handleGetStats(request, env, corsHeaders) {
  try {
    // Get total job count
    const totalJobs = await env.DB.prepare('SELECT COUNT(*) as count FROM jobs').first();
    
    // Get jobs by source
    const jobsBySource = await env.DB.prepare(`
      SELECT source, COUNT(*) as count 
      FROM jobs 
      GROUP BY source 
      ORDER BY count DESC
    `).all();
    
    // Get recent jobs (last 24 hours)
    const recentJobs = await env.DB.prepare(`
      SELECT COUNT(*) as count 
      FROM jobs 
      WHERE created_at > datetime('now', '-1 day')
    `).first();
    
    // Get recent exports
    const recentExports = await env.DB.prepare(`
      SELECT * FROM data_exports 
      ORDER BY exported_at DESC 
      LIMIT 5
    `).all();

    return new Response(JSON.stringify({
      total_jobs: totalJobs.count,
      jobs_by_source: jobsBySource.results,
      recent_jobs_24h: recentJobs.count,
      recent_exports: recentExports.results,
      generated_at: new Date().toISOString()
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error fetching stats:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to fetch statistics',
      message: error.message 
    }), { 
      status: 500, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// Handle manual data export
async function handleManualExport(request, env, corsHeaders) {
  try {
    const { date } = await request.json();
    const exportDate = date || new Date().toISOString().split('T')[0];
    
    await exportDataToR2(env, exportDate);
    
    return new Response(JSON.stringify({
      success: true,
      message: `Data export initiated for ${exportDate}`,
      export_date: exportDate
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error in manual export:', error);
    return new Response(JSON.stringify({ 
      error: 'Export failed',
      message: error.message 
    }), { 
      status: 500, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// Handle getting scraping jobs
async function handleGetScrapingJobs(request, env, corsHeaders) {
  try {
    const result = await env.DB.prepare(`
      SELECT * FROM scraping_jobs
      ORDER BY started_at DESC
      LIMIT 20
    `).all();
    
    return new Response(JSON.stringify({
      scraping_jobs: result.results,
      count: result.results.length
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error fetching scraping jobs:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to fetch scraping jobs',
      message: error.message 
    }), { 
      status: 500, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// Handle manual scrape trigger
async function handleTriggerScrape(request, env, corsHeaders) {
  try {
    const { source, max_jobs } = await request.json();
    
    const jobId = await triggerDailyScraping(env);
    
    return new Response(JSON.stringify({
      success: true,
      message: 'Scraping job triggered',
      job_id: jobId,
      webhook_url: `${new URL(request.url).origin}/api/scraping-webhook`
    }), {
      status: 202,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
    
  } catch (error) {
    console.error('Error triggering scrape:', error);
    return new Response(JSON.stringify({ 
      error: 'Failed to trigger scraping',
      message: error.message 
    }), { 
      status: 500, 
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
}

// Export the worker
export default {
  async fetch(request, env, ctx) {
    return handleRequest(request, env, ctx);
  },
  async scheduled(event, env, ctx) {
    return handleScheduled(event, env, ctx);
  }
};