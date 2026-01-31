import {
  Body,
  Container,
  Head,
  Hr,
  Html,
  Link,
  Preview,
  Row,
  Column,
  Section,
  Text,
} from '@react-email/components';

interface UserActivityReportProps {
  reportDate?: string;
  totalUsers?: number;
  newUsers7d?: number;
  activeUsers?: number;
  uniqueVisitors30d?: number;
  highIntentProspects?: Array<{
    email: string;
    mcpServer: string;
    clicks: number;
  }>;
  activeUsersList?: Array<{
    email: string;
    runs: number;
    successRate: number;
    lastRun: string;
  }>;
  atRiskUsers?: Array<{
    email: string;
    daysInactive: number;
    credits: number;
  }>;
  failedRuns?: Array<{
    email: string;
    error: string;
  }>;
  insights?: string[];
}

export const UserActivityReport = ({
  reportDate = 'January 25, 2026',
  totalUsers = 78,
  newUsers7d = 0,
  activeUsers = 26,
  uniqueVisitors30d = 156,
  highIntentProspects = [],
  activeUsersList = [
    { email: 'jeremy.scott.ross@gmail.com', runs: 877, successRate: 84.6, lastRun: 'Jan 24' },
    { email: 'catecean20@gmail.com', runs: 40, successRate: 50.0, lastRun: 'Jan 19' },
  ],
  atRiskUsers = [
    { email: 'ben@beneficial-intelligence.com', daysInactive: 11, credits: 100 },
    { email: 'andriyvovchak15@gmail.com', daysInactive: 12, credits: 100 },
  ],
  failedRuns = [
    { email: 'ravi@fulllist.ai', error: '409 runs, 0% success - URGENT' },
  ],
  insights = [
    '0 new signups in past 7 days',
    '14 MCP connect clicks (good interest)',
    '17% activation rate (156 visitors, 26 active)',
  ],
}: UserActivityReportProps) => (
  <Html>
    <Head />
    <Preview>DataGen User Activity Report - {reportDate}</Preview>
    <Body style={main}>
      <Container style={container}>
        {/* Header */}
        <Section style={header}>
          <Text style={brandText}>DATAGEN</Text>
          <Text style={titleText}>User Activity Report</Text>
          <Text style={dateText}>{reportDate}</Text>
        </Section>

        {/* Stats Grid */}
        <Section style={statsSection}>
          <Row>
            <Column style={statBox}>
              <Text style={statNumber}>{totalUsers}</Text>
              <Text style={statLabel}>TOTAL</Text>
            </Column>
            <Column style={statBox}>
              <Text style={statNumber}>{newUsers7d}</Text>
              <Text style={statLabel}>NEW 7D</Text>
            </Column>
            <Column style={statBox}>
              <Text style={statNumber}>{activeUsers}</Text>
              <Text style={statLabel}>ACTIVE</Text>
            </Column>
            <Column style={statBoxLast}>
              <Text style={statNumber}>{uniqueVisitors30d}</Text>
              <Text style={statLabel}>UNIQUE 30D</Text>
            </Column>
          </Row>
        </Section>

        <Hr style={divider} />

        {/* High Intent */}
        <Section style={section}>
          <Text style={sectionTitle}>High-Intent Prospects</Text>
          {highIntentProspects.length > 0 ? (
            highIntentProspects.map((prospect, i) => (
              <Row key={i} style={listItem}>
                <Column>
                  <Text style={itemEmail}>{prospect.email}</Text>
                  <Text style={itemMeta}>{prospect.mcpServer} - {prospect.clicks} clicks</Text>
                </Column>
              </Row>
            ))
          ) : (
            <Text style={emptyText}>None this period</Text>
          )}
        </Section>

        <Hr style={divider} />

        {/* Active Users */}
        <Section style={section}>
          <Text style={sectionTitle}>Active Users</Text>
          {activeUsersList.map((user, i) => (
            <Row key={i} style={listItem}>
              <Column>
                <Text style={itemEmail}>{user.email}</Text>
                <Text style={itemMeta}>{user.runs} runs - {user.successRate}% success - {user.lastRun}</Text>
              </Column>
            </Row>
          ))}
        </Section>

        <Hr style={divider} />

        {/* At Risk */}
        <Section style={section}>
          <Text style={sectionTitle}>At-Risk Users</Text>
          {atRiskUsers.map((user, i) => (
            <Row key={i} style={warningItem}>
              <Column>
                <Text style={itemEmail}>{user.email}</Text>
                <Text style={warningMeta}>{user.daysInactive}d inactive - {user.credits} credits</Text>
              </Column>
            </Row>
          ))}
        </Section>

        <Hr style={divider} />

        {/* Failed Runs */}
        <Section style={section}>
          <Text style={sectionTitle}>Failed Runs</Text>
          {failedRuns.length > 0 ? (
            failedRuns.map((run, i) => (
              <Row key={i} style={errorItem}>
                <Column>
                  <Text style={itemEmail}>{run.email}</Text>
                  <Text style={errorMeta}>{run.error}</Text>
                </Column>
              </Row>
            ))
          ) : (
            <Text style={emptyText}>None this period</Text>
          )}
        </Section>

        <Hr style={divider} />

        {/* Insights */}
        <Section style={insightsSection}>
          <Text style={sectionTitle}>Key Insights</Text>
          {insights.map((insight, i) => (
            <Text key={i} style={insightText}>- {insight}</Text>
          ))}
        </Section>

        {/* Footer */}
        <Section style={footer}>
          <Link href="https://datagen.dev" style={footerLink}>
            datagen.dev
          </Link>
        </Section>
      </Container>
    </Body>
  </Html>
);

export default UserActivityReport;

// Styles
const main = {
  backgroundColor: '#f4f4f5',
  fontFamily: 'Arial, Helvetica, sans-serif',
};

const container = {
  backgroundColor: '#ffffff',
  margin: '0 auto',
  maxWidth: '560px',
};

const header = {
  padding: '40px 32px 32px',
  textAlign: 'center' as const,
  borderBottom: '1px solid #e4e4e7',
};

const brandText = {
  margin: '0',
  fontSize: '11px',
  fontWeight: 'bold' as const,
  color: '#71717a',
  textTransform: 'uppercase' as const,
  letterSpacing: '1px',
};

const titleText = {
  margin: '8px 0 0',
  fontSize: '22px',
  fontWeight: '600',
  color: '#18181b',
};

const dateText = {
  margin: '8px 0 0',
  fontSize: '13px',
  color: '#71717a',
};

const statsSection = {
  padding: '0',
};

const statBox = {
  padding: '24px 8px',
  textAlign: 'center' as const,
  borderBottom: '1px solid #e4e4e7',
  borderRight: '1px solid #e4e4e7',
  width: '25%',
};

const statBoxLast = {
  ...statBox,
  borderRight: 'none',
};

const statNumber = {
  margin: '0',
  fontSize: '24px',
  fontWeight: '700',
  color: '#18181b',
};

const statLabel = {
  margin: '4px 0 0',
  fontSize: '10px',
  fontWeight: '600',
  color: '#a1a1aa',
  textTransform: 'uppercase' as const,
  letterSpacing: '0.5px',
};

const divider = {
  borderColor: '#e4e4e7',
  margin: '0',
};

const section = {
  padding: '28px 32px',
};

const sectionTitle = {
  margin: '0 0 16px',
  fontSize: '13px',
  fontWeight: '600',
  color: '#18181b',
};

const listItem = {
  marginBottom: '8px',
  padding: '8px 0',
  borderBottom: '1px solid #f4f4f5',
};

const warningItem = {
  marginBottom: '10px',
  padding: '10px 12px',
  backgroundColor: '#fef9c3',
};

const errorItem = {
  marginBottom: '10px',
  padding: '10px 12px',
  backgroundColor: '#fee2e2',
};

const itemEmail = {
  margin: '0',
  fontSize: '13px',
  fontWeight: '500',
  color: '#18181b',
};

const itemMeta = {
  margin: '2px 0 0',
  fontSize: '11px',
  color: '#71717a',
};

const warningMeta = {
  margin: '2px 0 0',
  fontSize: '11px',
  color: '#854d0e',
};

const errorMeta = {
  margin: '2px 0 0',
  fontSize: '11px',
  color: '#991b1b',
};

const emptyText = {
  margin: '0',
  fontSize: '12px',
  color: '#a1a1aa',
};

const insightsSection = {
  padding: '28px 32px',
  backgroundColor: '#fafafa',
};

const insightText = {
  margin: '0 0 8px',
  fontSize: '12px',
  color: '#52525b',
  lineHeight: '1.6',
};

const footer = {
  padding: '24px 32px',
  textAlign: 'center' as const,
  backgroundColor: '#fafafa',
};

const footerLink = {
  fontSize: '11px',
  color: '#71717a',
  textDecoration: 'none',
};
