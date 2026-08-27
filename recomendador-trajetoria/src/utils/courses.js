const courseNames = {
  307: 'Ciência da Computação',
  314: 'Sistemas de Informação',
}

export function courseName(code) {
  return courseNames[String(code)] || 'Curso não identificado'
}
