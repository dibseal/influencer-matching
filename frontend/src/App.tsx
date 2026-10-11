import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Alert,
  AppBar,
  Avatar,
  Box,
  Button,
  Chip,
  CircularProgress,
  CssBaseline,
  Divider,
  Drawer,
  IconButton,
  LinearProgress,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  MenuItem,
  Paper,
  Stack,
  TextField,
  ThemeProvider,
  Toolbar,
  Tooltip,
  Typography,
  createTheme,
} from '@mui/material';
import {
  AutoAwesome as AutoAwesomeIcon,
  BarChart as BarChartIcon,
  Campaign as CampaignIcon,
  Dashboard as DashboardIcon,
  Groups as GroupsIcon,
  Menu as MenuIcon,
  Refresh as RefreshIcon,
  SmartToy as SmartToyIcon,
  Wifi as WifiIcon,
  WifiOff as WifiOffIcon,
} from '@mui/icons-material';
import './App.css';
import {
  getApiBaseUrl,
  getHealth,
  getDashboardSummary,
  interpretCampaign,
  getBrands,
  getRecommendations,
  getEvaluationSummary,
  explainRecommendation,
  type ApiHealth,
  type DashboardSummary,
  type BrandOption,
  type MatchResponse,
  type EvaluationSummary,
} from './services/api';

type PageId = 'dashboard' | 'campaign' | 'matching' | 'evaluation';

const drawerWidth = 248;

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: { main: '#3157D5' },
    secondary: { main: '#64748b' },
    background: { default: '#F5F7FB', paper: '#FFFFFF' },
    success: { main: '#16856B' },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: { fontWeight: 750, letterSpacing: '-0.035em' },
    h5: { fontWeight: 700, letterSpacing: '-0.025em' },
    h6: { fontWeight: 700 },
    button: { textTransform: 'none', fontWeight: 650 },
  },
  shape: { borderRadius: 12 },
  components: {
    MuiPaper: {
      styleOverrides: {
        root: { backgroundImage: 'none' },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: { borderRadius: 10, paddingInline: 16 },
      },
    },
  },
});

const navItems: { id: PageId; label: string; icon: React.ReactNode }[] = [
  { id: 'dashboard', label: 'Overview', icon: <DashboardIcon /> },
  { id: 'campaign', label: 'Campaign builder', icon: <CampaignIcon /> },
  { id: 'matching', label: 'Influencer matching', icon: <GroupsIcon /> },
  { id: 'evaluation', label: 'Model evaluation', icon: <BarChartIcon /> },
];

function readableValue(value: unknown): React.ReactNode {
  if (value === null || value === undefined || value === '') return '—';
  if (typeof value === 'boolean' || typeof value === 'number' || typeof value === 'string') {
    return String(value);
  }
  if (Array.isArray(value)) {
    return (
      <Stack spacing={0.5}>
        {value.map((item, index) => (
          <Typography key={index} variant="body2">
            {typeof item === 'object' ? JSON.stringify(item, null, 2) : String(item)}
          </Typography>
        ))}
      </Stack>
    );
  }
  return (
    <Box component="pre" className="json-output">
      {JSON.stringify(value, null, 2)}
    </Box>
  );
}

function StatCard({
  label,
  value,
  caption,
  icon,
  tint,
}: {
  label: string;
  value: string;
  caption: string;
  icon: React.ReactNode;
  tint: string;
}) {
  return (
    <Paper className="stat-card" elevation={0}>
      <Stack direction="row" justifyContent="space-between" alignItems="flex-start" spacing={2}>
        <Box>
          <Typography variant="body2" color="text.secondary">{label}</Typography>
          <Typography variant="h4" sx={{ mt: 1, mb: 0.75 }}>{value}</Typography>
          <Typography variant="caption" color="text.secondary">{caption}</Typography>
        </Box>
        <Avatar sx={{ bgcolor: tint, color: '#3157D5', width: 44, height: 44, borderRadius: 3 }}>
          {icon}
        </Avatar>
      </Stack>
    </Paper>
  );
}

function App() {
  const [activePage, setActivePage] = useState<PageId>('dashboard');
  const [mobileNavOpen, setMobileNavOpen] = useState(false);
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [healthLoading, setHealthLoading] = useState(true);
  const [healthError, setHealthError] = useState('');
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [summaryError, setSummaryError] = useState('');
  const [summaryLoading, setSummaryLoading] = useState(true);
  const [campaignBrief, setCampaignBrief] = useState('');
  const [interpretation, setInterpretation] = useState<unknown>(null);
  const [interpretLoading, setInterpretLoading] = useState(false);
  const [interpretError, setInterpretError] = useState('');
  const [lastChecked, setLastChecked] = useState<Date | null>(null);
  const [brands, setBrands] = useState<BrandOption[]>([]);
  const [selectedBrandId, setSelectedBrandId] = useState('');
  const [matchingResults, setMatchingResults] = useState<MatchResponse | null>(null);
  const [matchingLoading, setMatchingLoading] = useState(false);
  const [matchingError, setMatchingError] = useState('');
  const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
  const [evaluationError, setEvaluationError] = useState('');
  const [evaluationLoading, setEvaluationLoading] = useState(false);
  const [explanationById, setExplanationById] = useState<Record<string, unknown>>({});
  const [explanationLoadingId, setExplanationLoadingId] = useState('');


  const activeLabel = useMemo(
    () => navItems.find((item) => item.id === activePage)?.label ?? 'Overview',
    [activePage],
  );

  const checkHealth = useCallback(async () => {
    setHealthLoading(true);
    setHealthError('');
    try {
      const result = await getHealth();
      setHealth(result);
      setLastChecked(new Date());
    } catch (error) {
      setHealth(null);
      setHealthError(error instanceof Error ? error.message : 'Unable to reach the API.');
    } finally {
      setHealthLoading(false);
    }
  }, []);

  useEffect(() => {
    void checkHealth();
  }, [checkHealth]);

  const loadDashboardSummary = useCallback(async () => {
    setSummaryLoading(true);
    setSummaryError('');
    try {
      const result = await getDashboardSummary();
      setSummary(result);
    } catch (error) {
      setSummary(null);
      setSummaryError(
        error instanceof Error ? error.message : 'Could not load dashboard statistics.',
      );
    } finally {
      setSummaryLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDashboardSummary();
  }, [loadDashboardSummary]);

  useEffect(() => {
    getBrands()
      .then((response) => {
        setBrands(response.brands);
        if (response.brands.length) setSelectedBrandId((current) => current || response.brands[0].brand_id);
      })
      .catch((error) => setMatchingError(error instanceof Error ? error.message : 'Could not load brands.'));
  }, []);

  const loadEvaluation = useCallback(async () => {
    setEvaluationLoading(true);
    setEvaluationError('');
    try {
      setEvaluation(await getEvaluationSummary());
    } catch (error) {
      setEvaluation(null);
      setEvaluationError(error instanceof Error ? error.message : 'Could not load evaluation summary.');
    } finally {
      setEvaluationLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadEvaluation();
  }, [loadEvaluation]);

  const handleFindInfluencers = async () => {
    setMatchingError('');
    setMatchingResults(null);
    if (!selectedBrandId) {
      setMatchingError('Select a brand before requesting recommendations.');
      return;
    }
    const raw = interpretation as { criteria?: Record<string, unknown> } | null;
    const criteria = raw?.criteria;
    if (!criteria) {
      setMatchingError('Interpret a campaign brief first.');
      return;
    }
    setMatchingLoading(true);
    try {
      const response = await getRecommendations(selectedBrandId, criteria, 10);
      setMatchingResults(response);
      setActivePage('matching');
    } catch (error) {
      setMatchingError(error instanceof Error ? error.message : 'Matching failed.');
    } finally {
      setMatchingLoading(false);
    }
  };

  const handleExplain = async (result: MatchResponse['results'][number]) => {
    const raw = interpretation as { criteria?: Record<string, unknown> } | null;
    if (!raw?.criteria) return;
    setExplanationLoadingId(result.influencer_id);
    setMatchingError('');
    try {
      const explanation = await explainRecommendation(raw.criteria, result.influencer_id, {
        match_score: result.match_score,
        audience_fit: result.audience_fit,
        engagement_quality: result.engagement_quality,
        brand_affinity: result.brand_affinity,
        historical_performance: result.historical_performance,
        cost_effectiveness: result.cost_effectiveness,
        estimated_cost: result.estimated_cost,
      });
      setExplanationById((current) => ({ ...current, [result.influencer_id]: explanation }));
    } catch (error) {
      setMatchingError(error instanceof Error ? error.message : 'Could not explain recommendation.');
    } finally {
      setExplanationLoadingId('');
    }
  };

  const handleInterpretCampaign = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setInterpretError('');
    setInterpretation(null);
    if (!campaignBrief.trim()) {
      setInterpretError('Enter a campaign brief before submitting.');
      return;
    }
    setInterpretLoading(true);
    try {
      const result = await interpretCampaign(campaignBrief.trim());
      setInterpretation(result);
    } catch (error) {
      setInterpretError(error instanceof Error ? error.message : 'Campaign interpretation failed.');
    } finally {
      setInterpretLoading(false);
    }
  };

  const navigate = (page: PageId) => {
    setActivePage(page);
    setMobileNavOpen(false);
  };

  const drawerContent = (
    <Box className="sidebar-inner">
      <Box className="brand-lockup">
        <Avatar className="brand-mark"><AutoAwesomeIcon /></Avatar>
        <Box>
          <Typography fontWeight={800} lineHeight={1.15}>InfluenceIQ</Typography>
          <Typography variant="caption" color="text.secondary">Creator intelligence</Typography>
        </Box>
      </Box>
      <Typography className="nav-section-label">WORKSPACE</Typography>
      <List disablePadding>
        {navItems.map((item) => (
          <ListItemButton
            key={item.id}
            selected={activePage === item.id}
            onClick={() => navigate(item.id)}
            className="nav-item"
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
      <Box className="sidebar-bottom">
        <Divider sx={{ mb: 2 }} />
        <Stack direction="row" spacing={1.25} alignItems="center">
          <Avatar sx={{ width: 34, height: 34, bgcolor: '#E5EBFF', color: '#3157D5' }}>
            <SmartToyIcon fontSize="small" />
          </Avatar>
          <Box sx={{ minWidth: 0 }}>
            <Typography variant="body2" fontWeight={700}>Hybrid recommendation</Typography>
            <Typography variant="caption" color="text.secondary">ML ranking + LLM insights</Typography>
          </Box>
        </Stack>
      </Box>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box className="app-shell">
        <Box component="nav" sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}>
          <Drawer
            variant="temporary"
            open={mobileNavOpen}
            onClose={() => setMobileNavOpen(false)}
            ModalProps={{ keepMounted: true }}
            sx={{ display: { xs: 'block', md: 'none' }, '& .MuiDrawer-paper': { width: drawerWidth } }}
          >
            {drawerContent}
          </Drawer>
          <Drawer
            variant="permanent"
            open
            sx={{
              display: { xs: 'none', md: 'block' },
              '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box', borderRight: '1px solid #E8ECF4' },
            }}
          >
            {drawerContent}
          </Drawer>
        </Box>

        <Box className="main-column">
          <AppBar position="sticky" elevation={0} className="topbar">
            <Toolbar className="topbar-toolbar">
              <IconButton
                edge="start"
                onClick={() => setMobileNavOpen(true)}
                sx={{ display: { md: 'none' }, mr: 1 }}
                aria-label="Open navigation"
              >
                <MenuIcon />
              </IconButton>
              <Box sx={{ flexGrow: 1 }}>
                <Typography variant="body2" color="text.secondary">Workspace / {activeLabel}</Typography>
                <Typography variant="h6" color="text.primary">{activeLabel}</Typography>
              </Box>
              <Tooltip title="Check backend connection">
                <Button
                  color="inherit"
                  startIcon={healthLoading ? <CircularProgress size={16} /> : health ? <WifiIcon /> : <WifiOffIcon />}
                  onClick={() => void checkHealth()}
                  className="connection-button"
                >
                  {healthLoading ? 'Checking API' : health ? 'API connected' : 'API unavailable'}
                </Button>
              </Tooltip>
            </Toolbar>
            {healthLoading && <LinearProgress />}
          </AppBar>

          <Box component="main" className="page-content">
            {healthError && (
              <Alert
                severity="error"
                action={<Button color="inherit" size="small" onClick={() => void checkHealth()}>Retry</Button>}
                sx={{ mb: 3 }}
              >
                {healthError} Confirm that FastAPI is running at {getApiBaseUrl()}.
              </Alert>
            )}

            {activePage === 'dashboard' && (
              <Stack spacing={3}>
                <Box className="page-heading">
                  <Box>
                    <Typography variant="h4">Campaign intelligence</Typography>
                    <Typography color="text.secondary" sx={{ mt: 1 }}>
                      Find creators who fit your audience, objectives and budget.
                    </Typography>
                  </Box>
                  <Button variant="contained" startIcon={<CampaignIcon />} onClick={() => navigate('campaign')}>
                    Create campaign
                  </Button>
                </Box>

                {summaryError && (
                  <Alert
                    severity="warning"
                    action={
                      <Button
                        color="inherit"
                        size="small"
                        onClick={() => void loadDashboardSummary()}
                      >
                        Retry
                      </Button>
                    }
                  >
                    {summaryError}
                  </Alert>
                )}

                <Box className="stat-grid">
                  <StatCard
                    label="Influencers indexed"
                    value={
                      summaryLoading
                        ? '…'
                        : summary
                          ? summary.influencers_indexed.toLocaleString()
                          : '—'
                    }
                    caption={summary ? 'Loaded from synthetic dataset' : 'Dataset count unavailable'}
                    icon={<GroupsIcon />}
                    tint="#E8EEFF"
                  />
                  <StatCard
                    label="Campaigns analyzed"
                    value={
                      summaryLoading
                        ? '…'
                        : summary
                          ? summary.campaigns_analyzed.toLocaleString()
                          : '—'
                    }
                    caption={summary ? 'Loaded from synthetic dataset' : 'Dataset count unavailable'}
                    icon={<CampaignIcon />}
                    tint="#E4F7EF"
                  />
                  <StatCard label="Matching engine" value="Hybrid" caption="Weighted ranking + semantic signals" icon={<BarChartIcon />} tint="#F0E8FF" />
                  <StatCard label="API status" value={health ? 'Online' : healthLoading ? 'Checking' : 'Offline'} caption={lastChecked ? `Checked ${lastChecked.toLocaleTimeString()}` : 'Waiting for health check'} icon={health ? <WifiIcon /> : <WifiOffIcon />} tint={health ? '#E4F7EF' : '#FFF0E8'} />
                </Box>

                <Box className="dashboard-grid">
                  <Paper className="content-card campaign-card" elevation={0}>
                    <Stack direction="row" alignItems="center" spacing={1.5} sx={{ mb: 1 }}>
                      <Avatar sx={{ bgcolor: '#E8EEFF', color: 'primary.main' }}><AutoAwesomeIcon /></Avatar>
                      <Box>
                        <Typography variant="h6">Start with a campaign brief</Typography>
                        <Typography variant="body2" color="text.secondary">Use natural language to define what success looks like.</Typography>
                      </Box>
                    </Stack>
                    <Typography color="text.secondary" sx={{ my: 2, lineHeight: 1.8 }}>
                      Describe the product, target audience, preferred social platform, campaign objective and budget. The LLM can turn the brief into structured criteria for the matching workflow.
                    </Typography>
                    <Button variant="contained" onClick={() => navigate('campaign')} endIcon={<CampaignIcon />}>Build a campaign</Button>
                  </Paper>

                  <Paper className="content-card" elevation={0}>
                    <Typography variant="h6">System readiness</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 2 }}>Connection status from the live health endpoint.</Typography>
                    <Stack spacing={2}>
                      <Stack direction="row" alignItems="center" spacing={1.5}>
                        <Box className={`status-dot ${health ? 'status-ok' : healthLoading ? 'status-pending' : 'status-error'}`} />
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography fontWeight={650}>FastAPI backend</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {healthLoading ? 'Checking /health…' : health ? 'Responding successfully' : 'Not reachable'}
                          </Typography>
                        </Box>
                        <Chip size="small" label={health ? 'Connected' : healthLoading ? 'Checking' : 'Offline'} color={health ? 'success' : 'default'} variant="outlined" />
                      </Stack>
                      <Divider />
                      <Stack direction="row" alignItems="center" spacing={1.5}>
                        <Box className={`status-dot ${brands.length ? 'status-ok' : 'status-pending'}`} />
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography fontWeight={650}>Matching endpoint</Typography>
                          <Typography variant="caption" color="text.secondary">{brands.length ? 'Brands and recommendations API available' : 'Checking matching API'}</Typography>
                        </Box>
                        <Chip size="small" label={brands.length ? 'Available' : 'Checking'} color={brands.length ? 'success' : 'default'} variant="outlined" />
                      </Stack>
                      <Divider />
                      <Stack direction="row" alignItems="center" spacing={1.5}>
                        <Box className={`status-dot ${evaluation ? 'status-ok' : 'status-pending'}`} />
                        <Box sx={{ flexGrow: 1 }}>
                          <Typography fontWeight={650}>Evaluation summary</Typography>
                          <Typography variant="caption" color="text.secondary">{evaluation ? 'Saved ranking metrics loaded' : 'Checking evaluation output'}</Typography>
                        </Box>
                        <Chip size="small" label={evaluation ? 'Available' : 'Checking'} color={evaluation ? 'success' : 'default'} variant="outlined" />
                      </Stack>
                    </Stack>
                  </Paper>
                </Box>
                <Typography variant="caption" color="text.secondary">
                  {health?.service ? `Connected service: ${health.service}` : 'Dashboard metrics will populate when summary endpoints are available.'}
                </Typography>
              </Stack>
            )}

            {activePage === 'campaign' && (
              <Stack spacing={3}>
                <Box className="page-heading">
                  <Box>
                    <Typography variant="h4">Campaign builder</Typography>
                    <Typography color="text.secondary" sx={{ mt: 1 }}>
                      Turn a campaign brief into structured requirements using the LLM.
                    </Typography>
                  </Box>
                  <Chip icon={<SmartToyIcon />} label="LLM-assisted" color="primary" variant="outlined" />
                </Box>
                <Box className="campaign-layout">
                  <Paper component="form" onSubmit={handleInterpretCampaign} className="content-card" elevation={0}>
                    <Typography variant="h6">Campaign brief</Typography>
                    <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, mb: 2.5 }}>
                      Include your product or category, audience, platform, objective, budget and any creator preferences.
                    </Typography>
                    <TextField
                      fullWidth
                      multiline
                      minRows={8}
                      maxRows={14}
                      label="Describe your campaign"
                      placeholder="Example: We are launching a skincare product for young adults in India. Find Instagram creators with authentic skincare content, strong engagement, and a mid-range budget. Our primary objective is awareness."
                      value={campaignBrief}
                      onChange={(event) => setCampaignBrief(event.target.value)}
                      disabled={interpretLoading}
                      required
                    />
                    {interpretError && <Alert severity="error" sx={{ mt: 2 }}>{interpretError}</Alert>}
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mt: 2 }}>
                      <Typography variant="caption" color="text.secondary">{campaignBrief.trim().length} characters</Typography>
                      <Button type="submit" variant="contained" disabled={interpretLoading || !campaignBrief.trim()} startIcon={interpretLoading ? <CircularProgress size={17} color="inherit" /> : <AutoAwesomeIcon />}>
                        {interpretLoading ? 'Interpreting…' : 'Interpret brief'}
                      </Button>
                    </Stack>
                  </Paper>
                  <Paper className="content-card" elevation={0}>
                    <Typography variant="h6">What happens next?</Typography>
                    <Stack spacing={2.5} sx={{ mt: 2.5 }}>
                      {[
                        ['01', 'Extract requirements', 'Identify category, audience, platform, objective and constraints.'],
                        ['02', 'Review the criteria', 'Verify the interpreted fields before matching creators.'],
                        ['03', 'Rank suitable creators', 'Use the ML matching endpoint to score eligible influencers.'],
                      ].map(([number, title, description]) => (
                        <Stack key={number} direction="row" spacing={2}>
                          <Avatar variant="rounded" sx={{ bgcolor: '#EEF2FF', color: 'primary.main', fontWeight: 800, width: 38, height: 38 }}>{number}</Avatar>
                          <Box>
                            <Typography fontWeight={700}>{title}</Typography>
                            <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>{description}</Typography>
                          </Box>
                        </Stack>
                      ))}
                    </Stack>
                  </Paper>
                </Box>
                {interpretation !== null && (
                  <Paper className="content-card" elevation={0}>
                    <Stack direction="row" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
                      <Box>
                        <Typography variant="h6">Interpreted campaign</Typography>
                        <Typography variant="body2" color="text.secondary">Response returned by the backend. Review it before using it for matching.</Typography>
                      </Box>
                      <Button startIcon={<RefreshIcon />} onClick={() => setInterpretation(null)}>Clear</Button>
                    </Stack>
                    <Box className="result-panel">{readableValue(interpretation)}</Box>
                    <Stack direction={{ xs: 'column', sm: 'row' }} spacing={2} sx={{ mt: 2 }} alignItems={{ sm: 'center' }}>
                      <TextField
                        select
                        fullWidth
                        label="Brand"
                        value={selectedBrandId}
                        onChange={(event) => setSelectedBrandId(event.target.value)}
                        helperText="Choose the brand whose affinity scores should be used."
                      >
                        {brands.map((brand) => (
                          <MenuItem key={brand.brand_id} value={brand.brand_id}>
                            {brand.brand_name} ({brand.primary_category})
                          </MenuItem>
                        ))}
                      </TextField>
                      <Button
                        variant="contained"
                        onClick={() => void handleFindInfluencers()}
                        disabled={matchingLoading || !selectedBrandId}
                        startIcon={matchingLoading ? <CircularProgress size={17} color="inherit" /> : <GroupsIcon />}
                      >
                        {matchingLoading ? 'Finding creators…' : 'Find influencers'}
                      </Button>
                    </Stack>
                    {matchingError && <Alert severity="error" sx={{ mt: 2 }}>{matchingError}</Alert>}
                  </Paper>
                )}
              </Stack>
            )}

            {activePage === 'matching' && (
              <Stack spacing={3}>
                <Box className="page-heading">
                  <Box>
                    <Typography variant="h4">Influencer matching</Typography>
                    <Typography color="text.secondary" sx={{ mt: 1 }}>Ranked creator recommendations and score evidence.</Typography>
                  </Box>
                  <Button variant="outlined" onClick={() => navigate('campaign')}>Back to campaign builder</Button>
                </Box>
                {matchingError && <Alert severity="error">{matchingError}</Alert>}
                {!matchingResults && (
                  <Paper className="content-card" elevation={0}>
                    <Typography variant="h6">No recommendations loaded</Typography>
                    <Typography color="text.secondary" sx={{ mt: 1 }}>Interpret a campaign brief and select a brand to generate ranked recommendations.</Typography>
                    <Button sx={{ mt: 2 }} variant="contained" onClick={() => navigate('campaign')}>Go to campaign builder</Button>
                  </Paper>
                )}
                {matchingResults && (
                  <>
                    <Alert severity="info">
                      {matchingResults.count} eligible creators returned by {matchingResults.ranking_method}. These scores use synthetic data and the configured weighted baseline.
                    </Alert>
                    {matchingResults.results.length === 0 && (
                      <Alert severity="warning">No influencers met the platform, follower and budget eligibility rules. Try a different campaign platform or budget.</Alert>
                    )}
                    {matchingResults.results.map((result, index) => (
                      <Paper key={result.influencer_id} className="content-card" elevation={0}>
                        <Stack direction={{ xs: 'column', md: 'row' }} justifyContent="space-between" spacing={2}>
                          <Box sx={{ flex: 1, minWidth: 0 }}>
                            <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap">
                              <Typography variant="h6">{index + 1}. {result.display_name || result.influencer_id}</Typography>
                              {result.verified && <Chip size="small" label="Verified" color="success" variant="outlined" />}
                              <Chip size="small" label={result.platform} />
                              <Chip size="small" label={result.primary_niche} />
                            </Stack>
                            <Typography color="text.secondary" sx={{ mt: 1 }}>
                              ID: {result.influencer_id} · {Number(result.follower_count).toLocaleString()} followers · {result.location}
                            </Typography>
                            <Typography sx={{ mt: 1 }}>
                              Estimated cost: {Number(result.estimated_cost).toLocaleString(undefined, { maximumFractionDigits: 2 })} · Engagement score: {Number(result.engagement_quality).toFixed(1)} / 100
                            </Typography>
                          </Box>
                          <Box sx={{ minWidth: 120, textAlign: { xs: 'left', md: 'right' } }}>
                            <Typography variant="h4" color="primary.main">{Number(result.match_score).toFixed(1)}</Typography>
                            <Typography variant="caption" color="text.secondary">Match score / 100</Typography>
                          </Box>
                        </Stack>
                        <Divider sx={{ my: 2 }} />
                        <Box sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr 1fr', md: 'repeat(5, 1fr)' }, gap: 2 }}>
                          {[
                            ['Audience fit', result.audience_fit],
                            ['Engagement', result.engagement_quality],
                            ['Brand affinity', result.brand_affinity],
                            ['Historical performance', result.historical_performance],
                            ['Cost effectiveness', result.cost_effectiveness],
                          ].map(([label, value]) => (
                            <Box key={String(label)}>
                              <Typography variant="caption" color="text.secondary">{label}</Typography>
                              <Typography fontWeight={700}>{Number(value).toFixed(1)} / 100</Typography>
                            </Box>
                          ))}
                        </Box>
                        <Button sx={{ mt: 2 }} variant="outlined" disabled={explanationLoadingId === result.influencer_id} onClick={() => void handleExplain(result)}>
                          {explanationLoadingId === result.influencer_id ? 'Generating explanation…' : 'Explain recommendation with AI'}
                        </Button>
                        {explanationById[result.influencer_id] !== undefined && (
                          <Box className="result-panel" sx={{ mt: 2 }}>{readableValue(explanationById[result.influencer_id])}</Box>
                        )}
                      </Paper>
                    ))}
                  </>
                )}
              </Stack>
            )}

            {activePage === 'evaluation' && (
              <Stack spacing={3}>
                <Box className="page-heading">
                  <Box>
                    <Typography variant="h4">Model evaluation</Typography>
                    <Typography color="text.secondary" sx={{ mt: 1 }}>Ranking quality measured against the saved synthetic relevance labels.</Typography>
                  </Box>
                  <Button variant="outlined" onClick={() => void loadEvaluation()} disabled={evaluationLoading}>
                    {evaluationLoading ? 'Refreshing…' : 'Refresh evaluation'}
                  </Button>
                </Box>
                {evaluationError && <Alert severity="warning">{evaluationError}</Alert>}
                {evaluation && evaluation.models && (
                  <>
                    <Alert severity="info">
                      Source: {evaluation.source || 'evaluation output'} · K = {evaluation.k || 10} · {evaluation.evaluation_cases ?? 'Unknown'} evaluation rows. These are synthetic benchmark results, not real-world campaign guarantees.
                    </Alert>
                    <Box className="stat-grid">
                      {evaluation.models.map((model) => (
                        <Paper key={model.model} className="content-card" elevation={0} sx={{ gridColumn: 'span 2' }}>
                          <Typography variant="h6">{model.model.replace(/_/g, ' ')}</Typography>
                          <Stack spacing={1.5} sx={{ mt: 2 }}>
                            {[
                              ['Precision@10', model.precision_at_10],
                              ['Recall@10', model.recall_at_10],
                              ['NDCG@10', model.ndcg_at_10],
                            ].map(([label, value]) => (
                              <Box key={String(label)}>
                                <Stack direction="row" justifyContent="space-between">
                                  <Typography variant="body2">{label}</Typography>
                                  <Typography fontWeight={700}>{(Number(value) * 100).toFixed(2)}%</Typography>
                                </Stack>
                                <Box sx={{ mt: 0.5, height: 8, bgcolor: 'grey.200', borderRadius: 5, overflow: 'hidden' }}>
                                  <Box sx={{ width: `${Math.max(0, Math.min(100, Number(value) * 100))}%`, height: '100%', bgcolor: 'primary.main' }} />
                                </Box>
                              </Box>
                            ))}
                          </Stack>
                        </Paper>
                      ))}
                    </Box>
                    {evaluation.note && <Typography variant="body2" color="text.secondary">{evaluation.note}</Typography>}
                  </>
                )}
                {!evaluation && !evaluationError && <Alert severity="info">Loading saved evaluation output…</Alert>}
                <Paper className="content-card" elevation={0}>
                  <Typography variant="h6">Interpretation guidance</Typography>
                  <Typography color="text.secondary" sx={{ mt: 1, lineHeight: 1.8 }}>
                    Compare ranking approaches on the same evaluation examples and relevance labels. The benchmark file shows semantic matching and weighted baseline metrics; the evaluation labels are synthetic, and unobserved influencer–campaign pairs should not automatically be treated as irrelevant.
                  </Typography>
                </Paper>
              </Stack>
            )}
          </Box>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
