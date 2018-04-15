export class Query{
	activity: string; 
	location: string; 
    description: string; 

    constructor(act: string, loc: string, des: string) {
        this.activity = act
        this.location = loc
        this.description = des
    }
}
