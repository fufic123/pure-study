<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
  <xsl:output method="html" doctype-system="about:legacy-compat" indent="yes"/>

  <xsl:template match="/users">
    <html lang="en">
      <head>
        <meta charset="utf-8"/>
        <title>Pure Study — User Report</title>
        <style>
          :root {
            --bg: #0a0a0a; --surface: #111; --border: #1f1f1f;
            --text: #f1f1f1; --text-dim: #a1a1aa; --text-mute: #71717a;
            --accent: #3b82f6; --green: #22c55e; --amber: #f59e0b; --red: #ef4444;
          }
          body {
            margin: 0; padding: 32px;
            background: var(--bg); color: var(--text);
            font-family: -apple-system, "Inter", system-ui, sans-serif;
            font-size: 14px; line-height: 1.5;
          }
          h1 { font-size: 26px; font-weight: 500; margin: 0 0 6px; letter-spacing: -0.02em; }
          .meta {
            font-family: ui-monospace, Menlo, monospace;
            color: var(--text-mute); font-size: 11px; margin-bottom: 24px;
            text-transform: uppercase; letter-spacing: 0.06em;
          }
          .summary {
            display: flex; gap: 16px; flex-wrap: wrap; margin-bottom: 24px;
          }
          .card {
            background: var(--surface); border: 1px solid var(--border);
            padding: 14px 18px; min-width: 140px;
          }
          .card-label {
            font-family: ui-monospace, Menlo, monospace; font-size: 10px;
            color: var(--text-mute); text-transform: uppercase; letter-spacing: 0.08em;
          }
          .card-value { font-size: 22px; font-weight: 500; margin-top: 4px; }
          table {
            width: 100%; border-collapse: collapse;
            background: var(--surface); border: 1px solid var(--border);
          }
          th, td { padding: 10px 14px; text-align: left; border-bottom: 1px solid var(--border); }
          th {
            font-size: 11px; font-weight: 500; text-transform: uppercase;
            letter-spacing: 0.06em; color: var(--text-mute);
            background: rgba(255,255,255,0.02);
          }
          tr:last-child td { border-bottom: none; }
          tr:hover td { background: rgba(255,255,255,0.02); }
          .status {
            display: inline-block; padding: 2px 8px; font-size: 11px;
            font-family: ui-monospace, Menlo, monospace; border: 1px solid;
          }
          .status-active { color: var(--green); border-color: rgba(34,197,94,0.4); }
          .status-inactive { color: var(--text-mute); border-color: var(--border); }
          .empty { color: var(--text-mute); font-style: italic; }
          .footer {
            margin-top: 24px; font-family: ui-monospace, Menlo, monospace;
            font-size: 10px; color: var(--text-mute);
          }
        </style>
      </head>
      <body>
        <h1>User Report</h1>
        <div class="meta">Generated via XML + XSLT · transformed server-side by lxml</div>

        <div class="summary">
          <div class="card">
            <div class="card-label">Total</div>
            <div class="card-value"><xsl:value-of select="count(user)"/></div>
          </div>
          <div class="card">
            <div class="card-label">Active</div>
            <div class="card-value"><xsl:value-of select="count(user[status='active'])"/></div>
          </div>
          <div class="card">
            <div class="card-label">Inactive</div>
            <div class="card-value"><xsl:value-of select="count(user[status='inactive'])"/></div>
          </div>
        </div>

        <table>
          <thead>
            <tr>
              <th>Full name</th>
              <th>Email</th>
              <th>Program</th>
              <th>Year</th>
              <th>Status</th>
              <th>Created</th>
            </tr>
          </thead>
          <tbody>
            <xsl:choose>
              <xsl:when test="count(user) = 0">
                <tr><td colspan="6" class="empty">No users yet.</td></tr>
              </xsl:when>
              <xsl:otherwise>
                <xsl:for-each select="user">
                  <xsl:sort select="created_at" order="descending"/>
                  <tr>
                    <td>
                      <xsl:choose>
                        <xsl:when test="string-length(full_name) &gt; 0">
                          <xsl:value-of select="full_name"/>
                        </xsl:when>
                        <xsl:otherwise><span class="empty">—</span></xsl:otherwise>
                      </xsl:choose>
                    </td>
                    <td><xsl:value-of select="email"/></td>
                    <td>
                      <xsl:choose>
                        <xsl:when test="string-length(program) &gt; 0">
                          <xsl:value-of select="program"/>
                        </xsl:when>
                        <xsl:otherwise><span class="empty">—</span></xsl:otherwise>
                      </xsl:choose>
                    </td>
                    <td>
                      <xsl:choose>
                        <xsl:when test="string-length(year_of_study) &gt; 0">
                          <xsl:value-of select="year_of_study"/>
                        </xsl:when>
                        <xsl:otherwise><span class="empty">—</span></xsl:otherwise>
                      </xsl:choose>
                    </td>
                    <td>
                      <span>
                        <xsl:attribute name="class">
                          status status-<xsl:value-of select="status"/>
                        </xsl:attribute>
                        <xsl:value-of select="status"/>
                      </span>
                    </td>
                    <td><xsl:value-of select="substring(created_at, 1, 10)"/></td>
                  </tr>
                </xsl:for-each>
              </xsl:otherwise>
            </xsl:choose>
          </tbody>
        </table>

        <div class="footer">
          Source: <code>GET /auth/users/report.xml</code> → XSLT (<code>/auth/users/report.xsl</code>) → HTML
        </div>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
