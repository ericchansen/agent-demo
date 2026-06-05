import type {ReactNode} from 'react';
import clsx from 'clsx';
import Heading from '@theme/Heading';
import styles from './styles.module.css';

type FeatureItem = {
  title: string;
  Svg: React.ComponentType<React.ComponentProps<'svg'>>;
  description: ReactNode;
};

const FeatureList: FeatureItem[] = [
  {
    title: 'CLI Surface',
    Svg: require('@site/static/img/undraw_docusaurus_tree.svg').default,
    description: (
      <>
        Prototype in GitHub Copilot CLI using MCP-connected Fabric and WorkIQ
        tools for fast iteration and low-friction demos.
      </>
    ),
  },
  {
    title: 'M365 Surface',
    Svg: require('@site/static/img/undraw_docusaurus_react.svg').default,
    description: (
      <>
        Publish the same business flow through Azure AI Foundry into M365
        Copilot and Teams with enterprise identity, OBO auth, and DOCX output.
      </>
    ),
  },
];

function Feature({title, Svg, description}: FeatureItem) {
  return (
    <div className={clsx('col col--6 margin-bottom--lg')}>
      <div className={clsx('card shadow--md', styles.featureCard)}>
        <div className="card__body text--center">
          <Svg className={styles.featureSvg} role="img" />
          <Heading as="h3">{title}</Heading>
          <p>{description}</p>
        </div>
      </div>
    </div>
  );
}

export default function HomepageFeatures(): ReactNode {
  return (
    <section className={styles.features}>
      <div className="container">
        <div className="row">
          {FeatureList.map((props, idx) => (
            <Feature key={idx} {...props} />
          ))}
        </div>
      </div>
    </section>
  );
}
