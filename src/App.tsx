/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

export interface LabStudy {
  id: string;
  name: string;
  image: string;
  description: string;
}

export const LAB_STUDIES: LabStudy[] = [
  {
    id: 'essencial',
    name: 'Essencial',
    image: 'assets/essencial.webp',
    description: 'Fundo limpo, luz suave e foco no produto. Funcional e confiável.',
  },
  {
    id: 'vibrante',
    name: 'Vibrante',
    image: 'assets/lab-vibrante.webp',
    description: 'Linguagem vibrante e brasileira. Saturação deliberada, respingos dinâmicos e energia tropical em primeiro plano.',
  },
  {
    id: 'sofisticada',
    name: 'Sofisticada',
    image: 'assets/lab-sofisticada.webp',
    description: 'Apresentação sofisticada e minimalista. Linhas puras, luz suave e equilíbrio gráfico para um posicionamento sutil e elegante.',
  },
];

export default function App() {
  return null;
}
