// add a tiny unique id generator to avoid key collisions
let __msgIdCounter = 0;
export const makeId = (prefix = "m") => `${prefix}-${++__msgIdCounter}-${Date.now()}`;
