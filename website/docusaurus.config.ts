import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'Fabric Sales Agent Accelerator',
  tagline:
    'Prototype with Copilot CLI. Deploy to M365 Copilot + Teams via Azure AI Foundry.',
  favicon: 'img/favicon.ico',
  future: {
    v4: true,
  },
  url: 'https://ericchansen.github.io',
  baseUrl: '/agent-demo/',
  organizationName: 'ericchansen',
  projectName: 'agent-demo',
  onBrokenLinks: 'throw',
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },
  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],
  themeConfig: {
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Fabric Sales Agent Accelerator',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Docs',
        },
        {
          href: 'https://github.com/ericchansen/agent-demo',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Overview',
              to: '/docs/intro',
            },
            {
              label: 'Architecture',
              to: '/docs/architecture',
            },
          ],
        },
        {
          title: 'Project',
          items: [
            {
              label: 'Repository',
              href: 'https://github.com/ericchansen/agent-demo',
            },
            {
              label: 'Setup Guide',
              to: '/docs/setup',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Eric Chansen. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
